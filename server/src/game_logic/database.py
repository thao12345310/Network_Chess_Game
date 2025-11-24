import sqlite3

DB_NAME = "chess_game.db"

def get_connection():
    return sqlite3.connect(DB_NAME)
