
import sys
import os
import json
import sqlite3

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import db_handler
import logic_wrapper
from logic_wrapper import validate_move, determine_result, update_game_result
from db_handler import create_game, register_user, get_player_id_by_username, get_game_info

def run_test():
    print("Setting up test...")
    
    # 1. Setup Users
    u1 = "test_white"
    u2 = "test_black"
    
    pid1 = get_player_id_by_username(u1)
    if not pid1:
        pid1 = register_user(u1, "password")
        
    pid2 = get_player_id_by_username(u2)
    if not pid2:
        pid2 = register_user(u2, "password")
        
    print(f"Players: {pid1} vs {pid2}")
    
    # 2. Create Game
    game_id = create_game(pid1, pid2, "BLITZ")
    print(f"Game Created: {game_id}")
    
    # 3. Define Fool's Mate Moves
    # 1. f3 e5
    # 2. g4 Qh4#
    moves = [
        ("f2f3", pid1),
        ("e7e5", pid2),
        ("g2g4", pid1),
        ("d8h4", pid2)
    ]
    
    # 4. Execute Moves via logic_wrapper logic simulation
    for i, (move, pid) in enumerate(moves):
        print(f"Executing move {i+1}: {move} by Player {pid}")
        
        # Construct request payload for logic_wrapper
        req = {
            "type": "MOVE", 
            "game_id": str(game_id), 
            "from": move[:2], 
            "to": move[2:]
        }
        
        # Capture stdout
        from io import StringIO
        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()
        
        # Inject request
        sys.stdin = StringIO(json.dumps(req))
        # We need to hack sys.argv or pass input differently because logic_wrapper uses sys.stdin.read() or argv
        # logic_wrapper.main() reads either argv[1:] or stdin.
        # Let's reset argv to ensure it reads stdin
        sys.argv = ["logic_wrapper.py"]
        
        try:
           logic_wrapper.main()
        except Exception as e:
           sys.stdout = old_stdout
           print(f"Exception: {e}")
           return

        sys.stdout = old_stdout
        output = mystdout.getvalue()
        
        try:
            resp = json.loads(output)
            print(f"Response: {resp.get('status')}, Result: {resp.get('game_result')}")
            
            if resp.get('status') == 'error':
                 print(f"Error Message: {resp.get('message')}")
                 
            if resp.get('game_result') == 'checkmate':
                print("SUCCESS: Checkmate detected!")
                
                # Check DB status
                g_info = get_game_info(str(game_id))
                # g_info: (game_id, white_id, black_id, mode, start_time, end_time, winner_id, status, current_fen)
                status = g_info[7]
                winner = g_info[6]
                print(f"DB Status: {status}, Winner ID: {winner}")
                
                if status == 'FINISHED' and winner == pid:
                    print("DB Verification: SUCCESS")
                else:
                     print(f"DB Verification: FAILED. Expected FINISHED/{pid}, got {status}/{winner}")
                
                return
                
        except json.JSONDecodeError:
            print(f"Failed to decode JSON: {output}")

    print("Test finished.")

if __name__ == "__main__":
    run_test()
