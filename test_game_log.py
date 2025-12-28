import sys
import os
import sqlite3
import unittest
import json
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'server', 'src', 'game_logic'))
sys.path.append(os.path.join(os.path.dirname(__file__)))

import db_handler
import init_db

TEST_DB_NAME = "test_game_log.db"

class TestGameLog(unittest.TestCase):
    
    def setUp(self):
        if os.path.exists(TEST_DB_NAME):
            os.remove(TEST_DB_NAME)

        def get_test_conn():
            return sqlite3.connect(TEST_DB_NAME)

        self.patcher1 = patch('db_handler.get_connection', side_effect=get_test_conn)
        self.patcher2 = patch('init_db.get_connection', side_effect=get_test_conn)
        
        self.patcher1.start()
        self.patcher2.start()
        
        init_db.init_db()
        
        # Populate DB
        conn = get_test_conn()
        cur = conn.cursor()
        
        # Players
        cur.execute("INSERT INTO Player (username, password, elo) VALUES ('WhitePlayer', 'pass', 1500)")
        p1_id = cur.lastrowid
        cur.execute("INSERT INTO Player (username, password, elo) VALUES ('BlackPlayer', 'pass', 1600)")
        p2_id = cur.lastrowid
        
        # Game
        cur.execute("""
            INSERT INTO Game (white_id, black_id, mode, status) 
            VALUES (?, ?, 'CLASSICAL', 'ONGOING')
        """, (p1_id, p2_id))
        self.game_id = cur.lastrowid
        
        conn.commit()
        conn.close()

        # Moves (calls db_handler which opens its own connection)
        db_handler.insert_move(self.game_id, p1_id, "e2e4")
        db_handler.insert_move(self.game_id, p2_id, "e7e5")

    def tearDown(self):
        self.patcher1.stop()
        self.patcher2.stop()
        if os.path.exists(TEST_DB_NAME):
            try:
                os.remove(TEST_DB_NAME)
            except:
                pass

    def test_get_game_details(self):
        details = db_handler.get_game_details(self.game_id)
        
        # Verify basic game info
        self.assertIsNotNone(details)
        self.assertEqual(details['game_id'], self.game_id)
        self.assertEqual(details['mode'], 'CLASSICAL')
        
        # Verify Players
        self.assertEqual(details['white_player']['username'], 'WhitePlayer')
        self.assertEqual(details['white_player']['elo'], 1500)
        self.assertEqual(details['black_player']['username'], 'BlackPlayer')
        self.assertEqual(details['black_player']['elo'], 1600)
        
        # Verify Moves
        self.assertEqual(len(details['moves']), 2)
        self.assertEqual(details['moves'][0], 'e2e4')
        self.assertEqual(details['moves'][1], 'e7e5')

if __name__ == '__main__':
    unittest.main()
