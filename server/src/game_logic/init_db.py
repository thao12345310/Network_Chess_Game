import sqlite3
from database import get_connection

# Starting position FEN
INITIAL_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

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
            current_fen TEXT DEFAULT 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
            FOREIGN KEY (white_id) REFERENCES Player(player_id),
            FOREIGN KEY (black_id) REFERENCES Player(player_id),
            FOREIGN KEY (winner_id) REFERENCES Player(player_id)
        )
    """)
    
    # Migration: Add current_fen column if it doesn't exist (for existing databases)
    try:
        cur.execute("ALTER TABLE Game ADD COLUMN current_fen TEXT DEFAULT 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'")
        conn.commit()
        print("✅ Added current_fen column to existing Game table")
    except sqlite3.OperationalError:
        pass  # Column already exists, no need to add
    
    # Update existing games that have NULL current_fen
    cur.execute("""
        UPDATE Game 
        SET current_fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
        WHERE current_fen IS NULL
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
