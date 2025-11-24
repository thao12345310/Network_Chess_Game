import socket
import json
import time

def test_client():
    time.sleep(1) # Wait for server
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('127.0.0.1', 5001))
        f = s.makefile('r', encoding='utf-8')
        
        # Test 1: Validate Move
        print("Testing validate_move...")
        req = {
            "action": "validate_move",
            "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
            "move": "e2e4"
        }
        s.sendall((json.dumps(req) + "\n").encode('utf-8'))
        resp = f.readline()
        print(f"Response: {resp.strip()}")
        
        time.sleep(0.5)

        # Test 2: Calculate ELO
        print("\nTesting calculate_elo...")
        req = {
            "action": "calculate_elo",
            "player_a_elo": 1200,
            "player_b_elo": 1200,
            "result_a": 1
        }
        s.sendall((json.dumps(req) + "\n").encode('utf-8'))
        resp = f.readline()
        print(f"Response: {resp.strip()}")
        
        s.close()
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    test_client()
