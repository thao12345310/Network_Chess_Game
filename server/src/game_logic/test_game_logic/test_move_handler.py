"""
Test script for MOVE handler (Option 2: Server manages game state)
Tests the new MOVE protocol where server gets FEN from database
"""

import socket
import json
import time
import sys
import os

# Add parent directory to path to import init_db
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from init_db import init_db, INITIAL_FEN
from database import get_connection

def setup_test_game():
    """Create a test game in database"""
    print("Setting up test game...")
    
    # Initialize database
    init_db()
    
    conn = get_connection()
    cur = conn.cursor()
    
    # Create test players
    cur.execute(
        "INSERT OR IGNORE INTO Player (username, password, elo) VALUES (?, ?, ?)",
        ("test_player1", "pass", 1200)
    )
    white_id = cur.lastrowid
    if not white_id:
        cur.execute("SELECT player_id FROM Player WHERE username = 'test_player1'")
        white_id = cur.fetchone()[0]
    
    cur.execute(
        "INSERT OR IGNORE INTO Player (username, password, elo) VALUES (?, ?, ?)",
        ("test_player2", "pass", 1200)
    )
    black_id = cur.lastrowid
    if not black_id:
        cur.execute("SELECT player_id FROM Player WHERE username = 'test_player2'")
        black_id = cur.fetchone()[0]
    
    # Create test game
    import datetime
    cur.execute(
        """
        INSERT INTO Game (white_id, black_id, mode, start_time, status, current_fen)
        VALUES (?, ?, 'CLASSICAL', ?, 'ONGOING', ?)
        """,
        (white_id, black_id, datetime.datetime.utcnow().isoformat(), INITIAL_FEN)
    )
    game_id = cur.lastrowid
    
    conn.commit()
    conn.close()
    
    print(f"✅ Created test game: game_id={game_id}, white_id={white_id}, black_id={black_id}")
    return game_id, white_id, black_id


def test_move_handler():
    """Test MOVE handler with server-managed game state"""
    time.sleep(1)  # Wait for server
    
    # Setup test game
    game_id, white_id, black_id = setup_test_game()
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('127.0.0.1', 5001))
        f = s.makefile('r', encoding='utf-8')
        
        print("\n" + "="*60)
        print("TEST 1: First Move (e2e4) - White's turn")
        print("="*60)
        
        # Test 1: First move (e2e4)
        req = {
            "type": "MOVE",
            "game_id": str(game_id),
            "from": "e2",
            "to": "e4"
        }
        print(f"Request: {json.dumps(req, indent=2)}")
        s.sendall((json.dumps(req) + "\n").encode('utf-8'))
        resp = f.readline()
        response = json.loads(resp.strip())
        print(f"Response: {json.dumps(response, indent=2)}")
        
        if response.get("status") == "success" and response.get("is_valid"):
            print("✅ Test 1 PASSED: Move validated and saved")
        else:
            print("❌ Test 1 FAILED")
            return False
        
        time.sleep(0.5)
        
        print("\n" + "="*60)
        print("TEST 2: Second Move (e7e5) - Black's turn")
        print("="*60)
        
        # Test 2: Second move (e7e5) - Black's turn
        req = {
            "type": "MOVE",
            "game_id": str(game_id),
            "from": "e7",
            "to": "e5"
        }
        print(f"Request: {json.dumps(req, indent=2)}")
        s.sendall((json.dumps(req) + "\n").encode('utf-8'))
        resp = f.readline()
        response = json.loads(resp.strip())
        print(f"Response: {json.dumps(response, indent=2)}")
        
        if response.get("status") == "success" and response.get("is_valid"):
            print("✅ Test 2 PASSED: Second move validated and saved")
        else:
            print("❌ Test 2 FAILED")
            return False
        
        time.sleep(0.5)
        
        print("\n" + "="*60)
        print("TEST 3: Invalid Move (e4e5) - Not a valid move")
        print("="*60)
        
        # Test 3: Invalid move
        req = {
            "type": "MOVE",
            "game_id": str(game_id),
            "from": "e4",
            "to": "e5"  # Invalid: can't move to occupied square
        }
        print(f"Request: {json.dumps(req, indent=2)}")
        s.sendall((json.dumps(req) + "\n").encode('utf-8'))
        resp = f.readline()
        response = json.loads(resp.strip())
        print(f"Response: {json.dumps(response, indent=2)}")
        
        if response.get("status") == "error" and not response.get("is_valid"):
            print("✅ Test 3 PASSED: Invalid move correctly rejected")
        else:
            print("❌ Test 3 FAILED: Should reject invalid move")
            return False
        
        time.sleep(0.5)
        
        print("\n" + "="*60)
        print("TEST 4: Missing game_id")
        print("="*60)
        
        # Test 4: Missing game_id
        req = {
            "type": "MOVE",
            "from": "e2",
            "to": "e4"
        }
        print(f"Request: {json.dumps(req, indent=2)}")
        s.sendall((json.dumps(req) + "\n").encode('utf-8'))
        resp = f.readline()
        response = json.loads(resp.strip())
        print(f"Response: {json.dumps(response, indent=2)}")
        
        if response.get("status") == "error":
            print("✅ Test 4 PASSED: Missing game_id correctly handled")
        else:
            print("❌ Test 4 FAILED")
            return False
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        
        s.close()
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("Starting MOVE handler tests...")
    print("Make sure the server is running on port 5001!")
    print()
    
    success = test_move_handler()
    sys.exit(0 if success else 1)

