
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
        if result.returncode != 0:
            print(f"❌ Logic fail: {result.stderr}")
        return json.loads(result.stdout)
    except Exception:
        return {}

def test_game_modes():
    print("Setting up test...")
    reset_db_run()
    
    # Create valid players manually for reference (white=1, black=2 approx)
    # The logic_wrapper create_game doesn't strictly enforce player existence DB fk unless we added FK constraints?
    # init_db.py HAS foreign keys. So we must create players first.
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO Player (username, password) VALUES ('Alice', 'pass')")
    p1 = cur.lastrowid
    cur.execute("INSERT INTO Player (username, password) VALUES ('Bob', 'pass')")
    p2 = cur.lastrowid
    conn.commit()
    conn.close()

    modes = [("BLITZ", 300.0), ("RAPID", 600.0), ("CLASSICAL", 1800.0)]
    
    for mode, expected_time in modes:
        print(f"\n--- Testing mode: {mode} ---")
        req = {
            "type": "create_game",
            "white_id": p1,
            "black_id": p2,
            "mode": mode
        }
        res = run_logic(req)
        
        if res.get('status') == 'success':
            gid = res.get('game_id')
            print(f"✅ Created Game ID {gid}")
            
            # Verify DB
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("SELECT mode, white_time, black_time, status FROM Game WHERE game_id=?", (gid,))
            row = cur.fetchone()
            conn.close()
            
            if row:
                db_mode, w_time, b_time, saved_status = row
                print(f"   DB Data: Mode={db_mode}, White={w_time}, Black={b_time}")
                
                if db_mode == mode and w_time == expected_time and b_time == expected_time:
                     print(f"✅ Verification Passed: Time is {expected_time}s")
                else:
                     print(f"❌ Verification FAILED. Expected {expected_time}, got {w_time}")
            else:
                 print("❌ Game not found in DB")
        else:
            print(f"❌ Failed to create game: {res}")

    # Test Invalid Mode
    print("\n--- Testing Invalid Mode ---")
    req = {
            "type": "create_game",
            "white_id": p1,
            "black_id": p2,
            "mode": "INVALID_MODE"
    }
    res = run_logic(req)
    if res.get('status') == 'error':
        print(f"✅ Correctly rejected invalid mode: {res.get('message')}")
    else:
        print(f"❌ Should have failed but got: {res}")

if __name__ == "__main__":
    test_game_modes()
