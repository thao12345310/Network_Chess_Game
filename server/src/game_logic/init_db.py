import sqlite3
from database import get_connection

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # Bảng Player
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Player (
            player_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            elo INTEGER DEFAULT 1000
        )
    """)

    # Bảng Game
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Game (
            game_id INTEGER PRIMARY KEY AUTOINCREMENT,
            white_id INTEGER NOT NULL,
            black_id INTEGER NOT NULL,
            mode TEXT CHECK(mode IN ('CLASSICAL', 'RAPID', 'BLITZ')),
            start_time TEXT,
            end_time TEXT,
            winner_id INTEGER,
            status TEXT CHECK(status IN ('ONGOING', 'FINISHED', 'CANCELLED')) DEFAULT 'ONGOING',
            FOREIGN KEY (white_id) REFERENCES Player(player_id),
            FOREIGN KEY (black_id) REFERENCES Player(player_id),
            FOREIGN KEY (winner_id) REFERENCES Player(player_id)
        )
    """)

    # Bảng Move
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Move (
            move_id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER NOT NULL,
            player_id INTEGER NOT NULL,
            move_notation TEXT NOT NULL,
            FOREIGN KEY (game_id) REFERENCES Game(game_id),
            FOREIGN KEY (player_id) REFERENCES Player(player_id)
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")

if __name__ == "__main__":
    init_db()
