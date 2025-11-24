import sys
import json
import traceback
import os

# Ensure we can import from the same directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from game_logic import validate_move, determine_result
from elo_system import calculate_elo
from db_handler import insert_move, get_moves, update_player_elo, update_game_result

def main():
    try:
        # Read JSON from stdin or command line argument
        # For simplicity with _popen, let's assume we pass the JSON string as an argument
        # But passing complex JSON as arg in Windows cmd can be tricky with escaping.
        # Better to read from stdin if possible, but _popen("cmd", "r") only allows reading stdout.
        # _popen("cmd", "w") allows writing to stdin.
        # Let's try reading from argv first as it's easier to implement in C++ side for a start 
        # (just string concatenation), provided we escape quotes.
        # Actually, standard way for IPC is stdin/stdout.
        
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
        action = req.get('action')
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

        else:
            response = {"status": "error", "message": f"Unknown action: {action}"}

        print(json.dumps(response))

    except Exception as e:
        # traceback.print_exc() # Don't print stacktrace to stdout to avoid corrupting JSON
        print(json.dumps({"status": "error", "message": str(e)}))

if __name__ == "__main__":
    main()
