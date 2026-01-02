
import sqlite3
import json
import subprocess
import os
import time
import sys

# Ensure we operate in the directory where this script and other logic files are
# Scripts are in parent directory of test_game_logic
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR) # server/src/game_logic

DB_NAME = "chess_game.db"
DB_PATH = os.path.join(PARENT_DIR, DB_NAME)
LOGIC_SCRIPT = os.path.join(PARENT_DIR, "logic_wrapper.py")

def reset_db():
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
        except PermissionError:
            print("⚠️ Could not remove DB, might be in use. Trying to overwrite anyway via init_db.")
    
    # Run init_db.py in the PARENT_DIR
    res = subprocess.run(
        [sys.executable, "init_db.py"], 
        cwd=PARENT_DIR,
        capture_output=True,
        text=True
    )
    if res.returncode != 0:
        print("❌ Init DB failed:", res.stderr)
    else:
        print("Database initialized.")

def run_logic(request_dict):
    """Run logic_wrapper.py with the given request and return response."""
    input_str = json.dumps(request_dict)
    # Run logic_wrapper.py in the PARENT_DIR
    result = subprocess.run(
        [sys.executable, LOGIC_SCRIPT],
        input=input_str,
        text=True,
        capture_output=True,
        cwd=PARENT_DIR
    )
    try:
        if result.returncode != 0:
             print("❌ Logic wrapper crashed/failed:", result.stderr)
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        print("Failed to decode JSON:", result.stdout)
        print("Stderr:", result.stderr)
        return {"status": "error", "message": "JSON Decode Error"}

def create_game():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    # Create two players
    cur.execute("INSERT INTO Player (username, password) VALUES ('Alice', 'pass')")
    p1_id = cur.lastrowid
    cur.execute("INSERT INTO Player (username, password) VALUES ('Bob', 'pass')")
    p2_id = cur.lastrowid
    
    # Create game
    cur.execute("""
        INSERT INTO Game (white_id, black_id, mode, white_time, black_time)
        VALUES (?, ?, 'CLASSICAL', 600.0, 600.0)
    """, (p1_id, p2_id))
    game_id = cur.lastrowid
    conn.commit()
    conn.close()
    return game_id, p1_id, p2_id

def test_time_control():
    print(f"Setting up test in {BASE_DIR}...")
    reset_db()
    game_id, p1, p2 = create_game()
    print(f"Game created: ID {game_id}. White: {p1}, Black: {p2}")

    # 1. White makes first move (e2e4)
    # Should set last_move_time, but NOT deduct time (or deduct negligible).
    print("\n--- Move 1: White e2e4 ---")
    req1 = {
        "type": "MOVE",
        "game_id": str(game_id),
        "from": "e2",
        "to": "e4"
    }
    res1 = run_logic(req1)
    if res1.get('status') != 'success':
        print("❌ Move 1 failed", res1)
        return

    # Check times
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT white_time, black_time, last_move_time FROM Game WHERE game_id=?", (game_id,))
    row = cur.fetchone()
    conn.close()
    
    if not row:
         print("❌ Could not fetch game data!")
         return

    print(f"DB State after Move 1: White={row[0]}, Black={row[1]}, LastMove={row[2]}")
    
    if row[2] is None:
        print("❌ last_move_time not set!")
    else:
        print("✅ last_move_time set.")

    # 2. Wait 2 seconds, then Black moves (e7e5)
    # Black's time should decrease by approx 2 seconds.
    print("\n--- Waiting 2 seconds... ---")
    time.sleep(2)
    
    print("--- Move 2: Black e7e5 ---")
    req2 = {
        "type": "MOVE",
        "game_id": str(game_id),
        "from": "e7",
        "to": "e5"
    }
    res2 = run_logic(req2)
    
    if res2.get('status') != 'success':
        print("❌ Move 2 failed", res2)
        return

    # Check times
    # Verify black time decreased
    prev_black = row[1] # 600.0
    new_black = res2.get('black_time')
    
    delta = prev_black - new_black if new_black else 0
    print(f"Black time: {new_black} (Delta: {delta})")
    
    if delta > 1.0: # allow some margin, at least 1s elapsed
        print(f"✅ Black time decreased correctly (by {delta}s)")
    else:
        print(f"❌ Black time did not decrease correctly! Got: {new_black}")

    # 3. Simulate Timeout
    # Set White's time to 0.1s manually
    print("\n--- Simulating White Timeout ---")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE Game SET white_time = 0.1 WHERE game_id=?", (game_id,))
    conn.commit()
    conn.close()
    
    time.sleep(1)
    
    # White tries to move (should fail with Timeout)
    print("--- Move 3: White d2d4 (should timeout) ---")
    req3 = {
        "type": "MOVE",
        "game_id": str(game_id),
        "from": "d2",
        "to": "d4"
    }
    res3 = run_logic(req3)
    print("Response:", res3)
    
    if res3.get('game_result') == 'timeout' or res3.get('message') == 'Timeout':
        print("✅ Timeout correctly detected!")
    else:
        print("❌ Timeout NOT detected or wrong winner.")

if __name__ == "__main__":
    test_time_control()
