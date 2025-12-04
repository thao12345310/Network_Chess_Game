import sys
import json
import traceback
import os

# Ensure we can import from the same directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from game_logic import validate_move, determine_result
from elo_system import calculate_elo
from db_handler import (
    insert_move, get_moves, update_player_elo, update_game_result,
    get_game_fen, update_game_fen, get_current_player_turn, get_game_info
)
import datetime

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
            new_elo = calculate_elo(p_a, p_b, res_a)
            response = {"status": "success", "new_elo": new_elo}
        
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
        
        elif action == 'update_game_result':
            gid = req.get('game_id')
            wid = req.get('winner_id')
            stat = req.get('status')
            end = req.get('end_time')
            update_game_result(gid, wid, stat, end)
            response = {"status": "success"}
        
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
                
                # Check if game exists first
                game_info = get_game_info(game_id_int)
                if not game_info:
                    response = {
                        "type": "MOVE_RESULT",
                        "status": "error",
                        "message": f"Game ID {game_id_int} does not exist. Please create a game first or use a valid game_id."
                    }
                    print(json.dumps(response))
                    return
                
                # Get current FEN from database
                current_fen = get_game_fen(game_id_int)
                
                # Convert format: "e2" + "e4" → "e2e4" (UCI format)
                move_uci = from_pos + to_pos
                
                # Validate move
                is_valid, next_fen = validate_move(current_fen, move_uci)
                
                if is_valid:
                    # Get current player's turn
                    current_player_id = get_current_player_turn(game_id_int)
                    
                    if not current_player_id:
                        # Provide more detailed error message using game_info we already have
                        white_id, black_id = game_info[1], game_info[2]
                        fen = game_info[8] if len(game_info) > 8 else None
                        if not fen:
                            error_msg = f"Game {game_id_int} exists but has no FEN. Game may be corrupted. Please reset database."
                        else:
                            parts = fen.split()
                            if len(parts) < 2:
                                error_msg = f"Game {game_id_int} has invalid FEN format: '{fen[:50]}...'"
                            else:
                                turn = parts[1]
                                error_msg = f"Game {game_id_int} exists but could not determine turn. FEN turn indicator: '{turn}' (expected 'w' or 'b'). White ID: {white_id}, Black ID: {black_id}."
                        
                        response = {
                            "type": "MOVE_RESULT",
                            "status": "error",
                            "message": error_msg
                        }
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
                        "game_result": game_result
                    }
                else:
                    # Invalid move
                    response = {
                        "type": "MOVE_RESULT",
                        "status": "error",
                        "is_valid": False,
                        "message": "Invalid move"
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
