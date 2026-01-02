
import sqlite3
import json
import subprocess
import os
import sys

# Ensure we operate in the directory where this script and other logic files are
# Scripts are in parent directory of test_game_logic
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR) # server/src/game_logic

DB_NAME = "chess_game.db"
DB_PATH = os.path.join(PARENT_DIR, DB_NAME)
LOGIC_SCRIPT = os.path.join(PARENT_DIR, "logic_wrapper.py")

def reset_db_run():
    # Use init_db.py to reset
    init_script = os.path.join(PARENT_DIR, "init_db.py")
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
        except PermissionError:
            pass # Try anyway
    subprocess.run([sys.executable, init_script], cwd=PARENT_DIR, capture_output=True)

def run_logic(request_dict):
    input_str = json.dumps(request_dict)
    result = subprocess.run(
        [sys.executable, LOGIC_SCRIPT],
        input=input_str,
        text=True,
        capture_output=True,
        cwd=PARENT_DIR
    )
    try:
        return json.loads(result.stdout)
    except Exception as e:
        print("Error decoding:", result.stdout)
        return {}

def test_replay():
    print("Setting up PGN test...")
    reset_db_run()
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO Player (username, password) VALUES ('Magnus', 'pass')")
    p1 = cur.lastrowid
    cur.execute("INSERT INTO Player (username, password) VALUES ('Hikaru', 'pass')")
    p2 = cur.lastrowid
    conn.commit()
    conn.close()

    # Create Game
    create_req = {
        "type": "create_game",
        "white_id": p1,
        "black_id": p2,
        "mode": "BLITZ"
    }
    create_res = run_logic(create_req)
    gid = create_res.get('game_id')
    print(f"Game Created: {gid}")

    # Make Moves: Fool's Mate
    # 1. f3 e5 2. g4 Qh4#
    moves = [
        ("f2", "f3"),
        ("e7", "e5"),
        ("g2", "g4"),
        ("d8", "h4")
    ]
    
    for i, (f, t) in enumerate(moves):
        req = {"type": "MOVE", "game_id": str(gid), "from": f, "to": t}
        res = run_logic(req)
        print(f"Move {i+1}: {res.get('status')} {res.get('game_result', '')}")

    # Get PGN
    print("\n--- Getting PGN ---")
    pgn_req = {"type": "get_pgn", "game_id": str(gid)}
    pgn_res = run_logic(pgn_req)
    
    if pgn_res.get('status') == 'success':
        pgn = pgn_res.get('pgn')
        print("✅ PGN Received:")
        print("--------------------------------------------------")
        print(pgn)
        print("--------------------------------------------------")
        
        # Validation
        if '[White "Magnus"]' in pgn and '[Black "Hikaru"]' in pgn:
             print("✅ Headers correct")
        else:
             print("❌ Headers missing/wrong")
             
        if "1. f3 e5 2. g4 Qh4#" in pgn:
             print("✅ Moves correct")
        else:
             print("❌ Moves missing/wrong")
             
        if '[Result "0-1"]' in pgn:
             print("✅ Result header correct")
        else:
             print("❌ Result header wrong")

    else:
        print("❌ Failed to get PGN:", pgn_res)

if __name__ == "__main__":
    test_replay()
