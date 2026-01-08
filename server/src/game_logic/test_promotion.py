
import sys
import os
import json

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import logic_wrapper
from db_handler import create_game, register_user, get_player_id_by_username

def run_test():
    print("Setting up Promotion test...")
    
    # 1. Setup Users
    u1 = "promo_white"
    u2 = "promo_black"
    
    pid1 = get_player_id_by_username(u1)
    if not pid1: pid1 = register_user(u1, "password")
        
    pid2 = get_player_id_by_username(u2)
    if not pid2: pid2 = register_user(u2, "password")
    
    # 2. Create Game
    game_id = create_game(pid1, pid2, "BLITZ")
    print(f"Game Created: {game_id}")
    
    # 3. Moves to achieve promotion
    # 1. h2h4 g7g5
    # 2. h4g5 f7f6 # Capture
    # ... shortcut ...
    # Let's use a simpler path or just trust logic?
    # Actually, we can just edit the FEN to be near promotion and validation.
    # But logic_wrapper uses current game state from DB.
    # So we must play valid moves or use update_game_fen (internal tool).
    
    # Let's just create a chain of moves.
    # White Pawn h2 -> h8
    moves = [
        ("h2h4", pid1), ("b7b6", pid2),
        ("h4h5", pid1), ("b6b5", pid2),
        ("h5h6", pid1), ("b5b4", pid2),
        ("h6g7", pid1), ("c8b7", pid2), # Capture on g7 (black pawn at g7? No, g7 is initial. h6xg7 is capture)
        # Wait, h6xg7 is valid if Black g7 is there.
        # Now pawn at g7.
        ("g7h8q", pid1) # Promotion!
    ]
    
    # Execute
    for i, (move, pid) in enumerate(moves):
        # ... logic ...
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
        
        sys.stdin = StringIO(json.dumps(req))
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
            if resp.get('status') == 'error':
                 print(f"Move {i+1} ({move}) Failed: {resp.get('message')}")
                 return
            print(f"Move {i+1} ({move}): Success. Result: {resp.get('game_result')}")
            
        except:
            print(f"Failed to decode: {output}")

    print("Test finished.")

if __name__ == "__main__":
    run_test()
