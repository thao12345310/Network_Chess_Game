import sys
import json
import traceback
import os

# Ensure we can import from the same directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from game_logic import validate_move, determine_result, export_pgn
from elo_system import calculate_elo
from db_handler import (
    insert_move, get_moves, update_player_elo, update_game_result,
    get_game_fen, update_game_fen, get_current_player_turn, get_game_info,
    get_player_rating, update_both_players_elo, get_game_details,
    add_to_lobby, remove_from_lobby, get_lobby_players,
    get_game_time, update_game_time, create_game
)
import datetime
import time

def main():
    try:
        # Read JSON from stdin or command line argument
        
        if len(sys.argv) > 1:
            # Join all args in case spaces split them (though we should quote properly)
            input_str = " ".join(sys.argv[1:])
        else:
            # Fallback to stdin
            input_str = sys.stdin.read()

        if not input_str.strip():
            print(json.dumps({"status": "error", "message": "No input provided"}))
            return

        req = json.loads(input_str)
        
        # Support both formats: "action" (from test) and "type" (from client)
        action = req.get('action') or req.get('type')
        response = {}

        if action == 'validate_move':
            fen = req.get('fen')
            move = req.get('move')
            is_valid, next_fen = validate_move(fen, move)
            response = {"status": "success", "is_valid": is_valid, "next_fen": next_fen}
        
        elif action == 'game_result':
            fen = req.get('fen')
            result = determine_result(fen)
            response = {"status": "success", "result": result}
        
        elif action == 'calculate_elo':
            p_a = req.get('player_a_elo')
            p_b = req.get('player_b_elo')
            res_a = req.get('result_a')
            new_a, new_b = calculate_elo(p_a, p_b, res_a)
            response = {"status": "success", "new_elo_a": new_a, "new_elo_b": new_b}

        elif action == 'process_match_elo':
            p_a_id = req.get('player_a_id')
            p_b_id = req.get('player_b_id')
            result_a = req.get('result_a') # 1, 0.5, 0

            # Fetch ratings
            rating_a = get_player_rating(p_a_id)
            rating_b = get_player_rating(p_b_id)

            # Calculate new ratings
            new_a, new_b = calculate_elo(rating_a, rating_b, result_a)

            # Update DB transactionally
            update_both_players_elo(p_a_id, new_a, p_b_id, new_b)

            response = {
                "status": "success",
                "player_a": {"old_elo": rating_a, "new_elo": new_a},
                "player_b": {"old_elo": rating_b, "new_elo": new_b}
            }
        
        elif action == 'update_elo':
            pid = req.get('player_id')
            elo = req.get('new_elo')
            update_player_elo(pid, elo)
            response = {"status": "success"}
        
        elif action == 'log_move':
            gid = req.get('game_id')
            pid = req.get('player_id')
            move = req.get('move')
            insert_move(gid, pid, move)
            response = {"status": "success"}
        
        elif action == 'get_replay':
            gid = req.get('game_id')
            moves = get_moves(gid)
            move_list = [m[1] for m in moves]
            response = {"status": "success", "moves": move_list}
        
        elif action == 'get_game_log':
            gid = req.get('game_id')
            game_details = get_game_details(gid)
            if game_details:
                response = {"status": "success", "game_log": game_details}
            else:
                response = {"status": "error", "message": "Game not found"}

        elif action == 'get_pgn':
            gid = req.get('game_id')
            game_details = get_game_details(gid)
            if game_details:
                # Need: moves list, white name, black name, result, date
                moves = game_details.get('moves', [])
                white = game_details['white_player']['username']
                black = game_details['black_player']['username']
                # Result format text needs to be standard? e.g. "1-0", "0-1", "1/2-1/2"
                # Database stores winner_id or NULL.
                # game_details has winner_id. 
                # Let's infer result string.
                wid = game_details.get('winner_id')
                status = game_details.get('status')
                
                result_str = "*"
                if status == 'FINISHED':
                    if wid == game_details['white_player'].get('player_id') or wid == game_details['white_player']['username']: 
                        # db_handler returns username/elo but game_details actually fetches from JOIN. 
                        # Let's check get_game_details implementation in db_handler.py to be sure what we have.
                        # It returns 'winner_id' as raw ID. we don't have player_ids in the sub-dicts easily?
                        # Wait, get_game_details does not return player_ids in white_player/black_player dicts, just username/elo.
                        # But it returns winner_id at top level.
                        # We need to map winner_id to white/black.
                        # We can fetch white_id/black_id from get_game_info or trust we can figure it out?
                        # Actually db_handler.get_game_details DOES NOT return white/black IDs.
                        # Let's fetch them separately or update db_handler?
                        # Easier: Use get_game_info to get IDs.
                        pass # resolved below
                    pass
                
                # Fetch simple game info for IDs
                g_info = get_game_info(gid) 
                if g_info:
                    # (game_id, white_id, black_id, mode, start_time, end_time, winner_id, status, current_fen, white_time, black_time, last_move_time)
                    # Note: db_handler get_game_info might need update if we added columns? 
                    # Yes, we added columns to DB but did we update get_game_info SELECT? 
                    # ... checking logic ... 
                    # We didn't update get_game_info SELECT statement in db_handler.py! 
                    # It selects specific columns: "SELECT game_id, white_id, black_id ..."
                    # So g_info indices are stable: 1=white_id, 2=black_id, 6=winner_id.
                    
                    white_id = g_info[1]
                    winner_id_raw = g_info[6]
                    
                    if status == 'FINISHED':
                        if winner_id_raw == white_id:
                            result_str = "1-0"
                        elif winner_id_raw is None:
                             result_str = "1/2-1/2" # Draw
                        else:
                             result_str = "0-1" # Black won
                
                start_time = game_details.get('start_time')
                if start_time and isinstance(start_time, str):
                    date_str = start_time.split('T')[0]
                else:
                    date_str = "????.??.??"
                
                pgn_str = export_pgn(moves, white, black, result_str, date_str)
                response = {"status": "success", "pgn": pgn_str}
            else:
                response = {"status": "error", "message": "Game not found"}

        elif action == 'update_game_result':
            gid = req.get('game_id')
            wid = req.get('winner_id')
            stat = req.get('status')
            end = req.get('end_time')
            update_game_result(gid, wid, stat, end)

            response = {"status": "success"}
        

        elif action == 'create_game':
            white_id = req.get('white_id')
            black_id = req.get('black_id')
            mode = req.get('mode', 'RAPID').upper()

            # Time limits in seconds
            mode_times = {
                "BLITZ": 300.0,      # 5 mins
                "RAPID": 600.0,      # 10 mins
                "CLASSICAL": 1800.0  # 30 mins
            }
            
            if mode not in mode_times:
                response = {"status": "error", "message": f"Invalid mode: {mode}. Allowed: BLITZ, RAPID, CLASSICAL"}
            else:
                time_limit = mode_times[mode]
                try:
                    new_game_id = create_game(white_id, black_id, mode, time_limit)
                    response = {
                        "status": "success", 
                        "game_id": new_game_id, 
                        "mode": mode,
                        "time_limit": time_limit
                    }
                except Exception as e:
                    response = {"status": "error", "message": str(e)}
        
        # ========== Lobby / Ready Players ==========

        elif action == 'join_lobby':
            pid = req.get('player_id')
            if not pid:
                response = {"status": "error", "message": "Missing player_id"}
            else:
                add_to_lobby(pid)
                response = {"status": "success", "message": "Added to lobby"}

        elif action == 'leave_lobby':
            pid = req.get('player_id')
            if not pid:
                response = {"status": "error", "message": "Missing player_id"}
            else:
                remove_from_lobby(pid)
                response = {"status": "success", "message": "Removed from lobby"}

        elif action == 'get_ready_players':
            players = get_lobby_players()
            response = {"status": "success", "players": players}

        # ========== Client Protocol: MOVE Handler ==========
        
        elif action == 'MOVE':
            # Format from client: {"type": "MOVE", "game_id": "123", "from": "e2", "to": "e4"}
            
            # Get request data
            game_id = req.get('game_id')
            from_pos = req.get('from')
            to_pos = req.get('to')
            
            # Validate required fields
            if not game_id or (isinstance(game_id, str) and game_id.strip() == ""):
                response = {
                    "type": "MOVE_RESULT",
                    "status": "error",
                    "message": "Missing or empty 'game_id' in MOVE request. Please set game_id first."
                }
                print(json.dumps(response))
                return
            
            if not from_pos or not to_pos:
                response = {
                    "type": "MOVE_RESULT",
                    "status": "error",
                    "message": "Missing 'from' or 'to' in MOVE request"
                }
                print(json.dumps(response))
                return
            
            try:
                game_id_int = int(game_id)
                
                
                # Check if game exists
                game_info = get_game_info(game_id_int)
                if not game_info:
                    response = {
                        "type": "MOVE_RESULT",
                        "status": "error",
                        "message": f"Game ID {game_id_int} does not exist."
                    }
                    print(json.dumps(response))
                    return

                # Time Control Logic
                white_id, black_id = game_info[1], game_info[2]
                current_fen = game_info[8] # Game info has FEN at index 8
                
                # Determine who is moving based on FEN (before the move)
                is_white_turn = True
                if current_fen:
                    parts = current_fen.split()
                    if len(parts) > 1 and parts[1] == 'b':
                        is_white_turn = False
                
                moving_player_id = white_id if is_white_turn else black_id
                
                # Get current time state
                white_time, black_time, last_move_ts_str = get_game_time(game_id_int)
                
                now = time.time()
                elapsed = 0.0
                
                if last_move_ts_str:
                    try:
                        last_ts = float(last_move_ts_str)
                        elapsed = now - last_ts
                    except ValueError:
                        elapsed = 0.0 # Should not happen if data is correct
                
                # Deduct time from the player who IS currently moving (they spent time thinking)
                # Note: For the very first move of the game (last_move_ts_str is None), usually we don't deduct,
                # or we deduct from game start. Let's assume no deduction for the very first move to be safe/simple,
                # or start clock when game starts.
                # Implementation: If last_move_ts_str is None, it's the first move.
                
                if last_move_ts_str: 
                    if is_white_turn:
                        white_time -= elapsed
                    else:
                        black_time -= elapsed
                
                # Check for timeout
                timeout = False
                if white_time <= 0:
                    white_time = 0
                    timeout = True
                    timeout_winner = black_id
                elif black_time <= 0:
                    black_time = 0
                    timeout = True
                    timeout_winner = white_id
                
                if timeout:
                    update_game_time(game_id_int, white_time, black_time, str(now))
                    update_game_result(
                        game_id_int,
                        timeout_winner,
                        'FINISHED',
                        datetime.datetime.utcnow().isoformat()
                    )
                    response = {
                        "type": "MOVE_RESULT",
                        "status": "success",
                        "is_valid": False, 
                        "message": "Timeout",
                        "game_result": "timeout",
                        "winner_id": timeout_winner,
                         "white_time": white_time,
                        "black_time": black_time
                    }
                    print(json.dumps(response))
                    return

                # Update time in DB (even if not timeout, we update the thinking time)
                # effectively "punching the clock"
                update_game_time(game_id_int, white_time, black_time, str(now))

                # --- Normal Move Logic Checks ---
                
                # Get current FEN from database (re-fetch not needed as we have it from game_info, 
                # but valid_move needs it. game_info's valid FEN is `current_fen`)
                if not current_fen:
                     current_fen = get_game_fen(game_id_int) 
                
                # Convert format: "e2" + "e4" → "e2e4" (UCI format)
                move_uci = from_pos + to_pos
                
                # Validate move
                is_valid, next_fen = validate_move(current_fen, move_uci)
                
                if is_valid:
                    # Get current player's turn (we effectively did this above, but keep consistency)
                    current_player_id = moving_player_id # reusing calculation
                    
                    if not current_player_id:
                         # Fallback error handling if something is weird
                        response = {"type": "MOVE_RESULT", "status": "error", "message": "Could not determine turn"}
                        print(json.dumps(response))
                        return
                    
                    # Save move to database
                    insert_move(game_id_int, current_player_id, move_uci)
                    
                    # Update FEN in database
                    update_game_fen(game_id_int, next_fen)
                    
                    # Check game result
                    game_result = determine_result(next_fen)
                    
                    # Update game status if game ended
                    if game_result in ['checkmate', 'draw']:
                        winner_id = None
                        if game_result == 'checkmate':
                            # Winner is the player who just moved
                            winner_id = current_player_id
                        
                        update_game_result(
                            game_id_int,
                            winner_id,
                            'FINISHED',
                            datetime.datetime.utcnow().isoformat()
                        )
                    
                    # Success response
                    response = {
                        "type": "MOVE_RESULT",
                        "status": "success",
                        "is_valid": True,
                        "next_fen": next_fen,
                        "game_result": game_result,
                        "white_time": white_time,
                        "black_time": black_time
                    }
                else:
                    # Invalid move
                    # We might want to revert the time deduction? 
                    # In official chess, invalid move adds time penalty or is just rejected.
                    # Online, usually we don't deduct time for invalid inputs immediately (latency),
                    # or we do? Let's keep the time deduction because they spent time thinking and sent a bad move.
                    response = {
                        "type": "MOVE_RESULT",
                        "status": "error",
                        "is_valid": False,
                        "message": "Invalid move",
                        "white_time": white_time,
                        "black_time": black_time
                    }
                    
            except ValueError:
                response = {
                    "type": "MOVE_RESULT",
                    "status": "error",
                    "message": "Invalid game_id format. Must be a number."
                }
            except Exception as e:
                response = {
                    "type": "MOVE_RESULT",
                    "status": "error",
                    "message": f"Error processing move: {str(e)}"
                }

        else:
            response = {"status": "error", "message": f"Unknown action: {action}"}

        print(json.dumps(response))

    except Exception as e:
        # traceback.print_exc() # Don't print stacktrace to stdout to avoid corrupting JSON
        print(json.dumps({"status": "error", "message": str(e)}))

if __name__ == "__main__":
    main()
