import subprocess
import json
import sys
import os
import time

# Paths
SERVER_DIR = r"d:\Network_Chess_Game\server\src\game_logic"
LOGIC_WRAPPER = os.path.join(SERVER_DIR, "logic_wrapper.py")

def run_logic(request):
    cmd = [sys.executable, LOGIC_WRAPPER]
    process = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=SERVER_DIR
    )
    stdout, stderr = process.communicate(input=json.dumps(request))
    if stderr:
        print(f"STDERR: {stderr}")
    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        print(f"Invalid JSON: {stdout}")
        return None

def main():
    print("--- Setting up Test Game ---")
    # 1. Create Game (Blitz 5 min -> 300s)
    # We need valid player IDs. Assume 1 and 2 exist or register them.
    # Actually, we can just use create_game, if it fails we might need to register.
    # Let's try registering 'TestA' and 'TestB'
    
    r1 = run_logic({"action": "REGISTER", "username": "TestTimeoutA", "password": "pw"})
    id_a = r1.get('payload', {}).get('user_id') or 1
    
    r2 = run_logic({"action": "REGISTER", "username": "TestTimeoutB", "password": "pw"})
    id_b = r2.get('payload', {}).get('user_id') or 2
    
    print(f"Players: {id_a} vs {id_b}")
    
    # Create Game
    create_req = {
        "action": "create_game", 
        "white_id": id_a, 
        "black_id": id_b, 
        "mode": "BLITZ"
    }
    game_res = run_logic(create_req)
    if not game_res or game_res.get('status') != 'success':
        print("Failed to create game:", game_res)
        return
        
    game_id = game_res['game_id']
    print(f"Game Created: {game_id}. Mode: {game_res['mode']} (Should be 300s)")

    # 2. Simulate User A (White) moving
    # Logic wrapper updates time.
    # To test timeout, we need to artificially drain time? 
    # Or we can just wait? 300s is too long.
    # We can manually update the database? logic_wrapper doesn't expose "set_time".
    # BUT, logic_wrapper calculates elapsed time based on `last_move_time`.
    # If we made a move 301 seconds ago...
    
    # We can't easily fake `last_move_time` via logic_wrapper without direct DB access.
    # However, create_game sets `last_move_time` to NOW.
    # If we verify that CLAIM works generically, that's enough.
    # But `time_left` check will fail if we just created it.
    
    # HACK: Directly modify DB to set a past timestamp?
    # Or modify logic_wrapper temporarily? No.
    # Use python sqlite3 to hack the DB.
    
    print("--- Hacking DB to simulate time passage ---")
    import sqlite3
    db_path = os.path.join(SERVER_DIR, "chess_game.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Set last_move_time to 10 mins ago (600s)
    # White has 300s. Pass 600s -> White should be -300s.
    past_ts = time.time() - 600
    cur.execute("UPDATE Game SET last_move_time = ? WHERE game_id = ?", (str(past_ts), game_id))
    conn.commit()
    conn.close()
    print("DB Updated: last_move_time set to 600s ago")
    
    # 3. Simulate CLAIM Timeout (Player B claims White timed out)
    print("--- Claiming Timeout ---")
    # It is White's turn (start of game).
    # Sender doesn't strictly matter for the CLAIM action logic I wrote (it checks turn),
    # but `logic_wrapper` expects `from` and `to`.
    # My code used `current_player_id` which it derives from FEN.
    # So `insert_move` checks turn. Wait.
    # `validate_move` checks turn? 
    # My CLAIM logic is BEFORE `validate_move`.
    # But I check `current_player_id`.
    # `current_player_id` is derived from `moving_player_id` which is derived from FEN.
    # Game start FEN -> White to move.
    # So `current_player_id` will be `white_id`.
    
    claim_req = {
        "action": "MOVE",
        "game_id": str(game_id),
        "from": "CLAIM",
        "to": "TIMEOUT"
    }
    
    res = run_logic(claim_req)
    print("Claim Response:", json.dumps(res, indent=2))
    
    if res.get('game_result') == 'timeout' and res.get('winner_id') == id_b:
        print("SUCCESS: Timeout claimed correctly. Winner is Black.")
    else:
        print("FAILURE: Timeout not claimed or wrong result.")

if __name__ == "__main__":
    main()
