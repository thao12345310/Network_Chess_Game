import sys
import os
import sqlite3
import unittest
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'server', 'src', 'game_logic'))
sys.path.append(os.path.join(os.path.dirname(__file__)))

# Import modules to test
# We need to mock database.get_connection BEFORE importing db_handler if it was using it globally, 
# but it uses it inside functions, so patching is fine.

import elo_system
import db_handler
import init_db

# Mock DB connection
TEST_DB_NAME = "test_elo_update.db"

class TestELOSystem(unittest.TestCase):
    
    def setUp(self):
        # Clean up any existing file
        if os.path.exists(TEST_DB_NAME):
            os.remove(TEST_DB_NAME)

        # Patch get_connection to return a NEW connection to our test DB file
        def get_test_conn():
            return sqlite3.connect(TEST_DB_NAME)

        import database
        self.patcher1 = patch('db_handler.get_connection', side_effect=get_test_conn)
        self.patcher2 = patch('init_db.get_connection', side_effect=get_test_conn)
        
        self.patcher1.start()
        self.patcher2.start()
        
        # Initialize schema
        init_db.init_db()
        
        # Create test players
        conn = get_test_conn()
        cur = conn.cursor()
        cur.execute("INSERT INTO Player (username, password, elo) VALUES ('p1', 'pass', 1200)")
        cur.execute("INSERT INTO Player (username, password, elo) VALUES ('p2', 'pass', 1400)")
        conn.commit()
        conn.close()

    def tearDown(self):
        self.patcher1.stop()
        self.patcher2.stop()
        if os.path.exists(TEST_DB_NAME):
            try:
                os.remove(TEST_DB_NAME)
            except PermissionError:
                pass # Might still be open if test failed mid-way, but that's okay for temp file

    def test_k_factor(self):
        self.assertEqual(elo_system.get_k_factor(1200), 24)
        self.assertEqual(elo_system.get_k_factor(1299), 24)
        self.assertEqual(elo_system.get_k_factor(1300), 32)
        self.assertEqual(elo_system.get_k_factor(1400), 32)

    def test_calculate_elo_p1_win(self):
        # P1 (1200, K=24) vs P2 (1400, K=32)
        # P1 Wins (1.0)
        
        # Expected A = 1 / (1 + 10^((1400-1200)/400)) = 1 / (1 + 10^0.5) = 1 / (1 + 3.162) = 1/4.162 = 0.240
        # Expected B = 0.760
        
        # New A = 1200 + 24 * (1 - 0.240) = 1200 + 24 * 0.76 = 1200 + 18.24 = 1218
        # New B = 1400 + 32 * (0 - 0.760) = 1400 - 24.32 = 1376
        
        new_a, new_b = elo_system.calculate_elo(1200, 1400, 1.0)
        
        # Allow small rounding diffs, but our logic uses round()
        self.assertAlmostEqual(new_a, 1218, delta=1)
        self.assertAlmostEqual(new_b, 1376, delta=1)

    def test_calculate_elo_draw(self):
        # P1 (1200, K=24) vs P2 (1400, K=32)
        # Draw (0.5)
        
        # Exp A = 0.24, Exp B = 0.76
        # New A = 1200 + 24 * (0.5 - 0.24) = 1200 + 24 * 0.26 = 1200 + 6.24 = 1206
        # New B = 1400 + 32 * (0.5 - 0.76) = 1400 + 32 * (-0.26) = 1400 - 8.32 = 1392
        
        new_a, new_b = elo_system.calculate_elo(1200, 1400, 0.5)
        self.assertAlmostEqual(new_a, 1206, delta=1)
        self.assertAlmostEqual(new_b, 1392, delta=1)

    def test_db_update(self):
        # Verify initial state
        p1_elo = db_handler.get_player_rating(1)
        p2_elo = db_handler.get_player_rating(2)
        self.assertEqual(p1_elo, 1200)
        self.assertEqual(p2_elo, 1400)
        
        # Process update
        new_a, new_b = elo_system.calculate_elo(p1_elo, p2_elo, 1.0)
        db_handler.update_both_players_elo(1, new_a, 2, new_b)
        
        # Verify update
        p1_elo_new = db_handler.get_player_rating(1)
        p2_elo_new = db_handler.get_player_rating(2)
        
        self.assertEqual(p1_elo_new, new_a)
        self.assertEqual(p2_elo_new, new_b)
        self.assertNotEqual(p1_elo_new, 1200)

if __name__ == '__main__':
    unittest.main()
