import sqlite3

import os

# Use absolute path to ensure we always use the same DB file regardless of where the script is run from
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "chess_game.db")

def get_connection():
    return sqlite3.connect(DB_NAME)
