import sqlite3
from database import get_connection
from init_db import INITIAL_FEN


def insert_move(game_id, player_id, move_notation):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO Move (game_id, player_id, move_notation)
        VALUES (?, ?, ?)
        """,
        (game_id, player_id, move_notation),
    )
    conn.commit()
    conn.close()


def create_game(white_id, black_id, mode, time_limit):
    """
    Create a new game with specified mode and time limit.
    time_limit should be in seconds.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO Game (white_id, black_id, mode, white_time, black_time, status)
        VALUES (?, ?, ?, ?, ?, 'ONGOING')
        """,
        (white_id, black_id, mode, time_limit, time_limit)
    )
    game_id = cur.lastrowid
    conn.commit()
    conn.close()
    return game_id



def get_moves(game_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT move_id, move_notation FROM Move WHERE game_id = ? ORDER BY move_id",
        (game_id,),
    )
    moves = cur.fetchall()
    conn.close()
    return moves


def update_player_elo(player_id, new_elo):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE Player SET elo = ? WHERE player_id = ?",
        (new_elo, player_id),
    )
    conn.commit()
    conn.close()


def get_player_rating(player_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT elo FROM Player WHERE player_id = ?", (player_id,))
    result = cur.fetchone()
    conn.close()
    if result:
        return result[0]
    return 1200 # Default if not found, though ideally should exist


def update_both_players_elo(player_a_id, new_elo_a, player_b_id, new_elo_b):
    """
    Updates ELO for two players within a single transaction.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "UPDATE Player SET elo = ? WHERE player_id = ?",
            (new_elo_a, player_a_id),
        )
        cur.execute(
            "UPDATE Player SET elo = ? WHERE player_id = ?",
            (new_elo_b, player_b_id),
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def update_game_result(game_id, winner_id, status, end_time):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE Game
        SET winner_id = ?, status = ?, end_time = ?
        WHERE game_id = ?
        """,
        (winner_id, status, end_time, game_id),
    )
    conn.commit()
    conn.close()


# ========== Game State Management Functions ==========

def get_game_fen(game_id):
    """
    Get current FEN (board state) of a game.
    Returns INITIAL_FEN if game not found or FEN is NULL.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT current_fen FROM Game WHERE game_id = ?",
        (game_id,)
    )
    result = cur.fetchone()
    conn.close()
    
    if result and result[0]:
        return result[0]
    return INITIAL_FEN


def update_game_fen(game_id, new_fen):
    """
    Update current FEN (board state) of a game after a move.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE Game SET current_fen = ? WHERE game_id = ?",
        (new_fen, game_id)
    )
    conn.commit()
    conn.close()



def update_game_time(game_id, white_time, black_time, last_move_time):
    """
    Update remaining time for both players and the last move timestamp.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE Game 
        SET white_time = ?, black_time = ?, last_move_time = ?
        WHERE game_id = ?
        """,
        (white_time, black_time, last_move_time, game_id)
    )
    conn.commit()
    conn.close()


def get_game_time(game_id):
    """
    Get current time status of a game.
    Returns tuple: (white_time, black_time, last_move_time)
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT white_time, black_time, last_move_time FROM Game WHERE game_id = ?",
        (game_id,)
    )
    result = cur.fetchone()
    conn.close()
    return result if result else (600.0, 600.0, None)


def get_current_player_turn(game_id):
    """
    Get player_id of the player whose turn it is to move.
    Based on FEN turn indicator (w = white, b = black).
    Returns None if game not found or invalid.
    """
    # First check if game exists
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT white_id, black_id, current_fen FROM Game WHERE game_id = ?",
        (game_id,)
    )
    result = cur.fetchone()
    conn.close()
    
    if not result:
        return None  # Game not found
    
    white_id, black_id, fen = result
    
    # If FEN is None or empty, return None
    if not fen:
        return None
    
    # Parse FEN to get turn: "rnbqkbnr/... w ..." or "rnbqkbnr/... b ..."
    parts = fen.split()
    if len(parts) < 2:
        return None
    
    turn_char = parts[1]  # 'w' or 'b'
    
    # Return player_id based on turn
    if turn_char == 'w':
        return white_id
    elif turn_char == 'b':
        return black_id
    
    return None


def get_game_info(game_id):
    """
    Get full game information including current FEN.
    Returns tuple: (game_id, white_id, black_id, mode, start_time, end_time, 
                    winner_id, status, current_fen)
    Returns None if game not found.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT game_id, white_id, black_id, mode, start_time, end_time,
               winner_id, status, current_fen
        FROM Game
        WHERE game_id = ?
        """,
        (game_id,)
    )
    game = cur.fetchone()
    conn.close()
    return game


def get_game_details(game_id):
    """
    Get full game details for logging/replay.
    Returns dictionary with game info, players, and moves.
    """
    conn = get_connection()
    cur = conn.cursor()
    
    # Get Game and Player info
    cur.execute(
        """
        SELECT 
            g.game_id, g.mode, g.start_time, g.end_time, g.status, g.winner_id,
            p1.username as white_username, p1.elo as white_elo,
            p2.username as black_username, p2.elo as black_elo
        FROM Game g
        JOIN Player p1 ON g.white_id = p1.player_id
        JOIN Player p2 ON g.black_id = p2.player_id
        WHERE g.game_id = ?
        """,
        (game_id,)
    )
    game_row = cur.fetchone()
    
    if not game_row:
        conn.close()
        return None
        
    # Get Moves
    cur.execute(
        "SELECT move_notation from Move WHERE game_id = ? ORDER BY move_id ASC",
        (game_id,)
    )
    moves = [row[0] for row in cur.fetchall()]
    
    conn.close()
    
    return {
        "game_id": game_row[0],
        "mode": game_row[1],
        "start_time": game_row[2],
        "end_time": game_row[3],
        "status": game_row[4],
        "winner_id": game_row[5],
        "white_player": {"username": game_row[6], "elo": game_row[7]},
        "black_player": {"username": game_row[8], "elo": game_row[9]},
        "moves": moves
    }


# ========== Lobby / Ready Players Management ==========

def add_to_lobby(player_id):
    """
    Add a player to the ready lobby.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("INSERT OR IGNORE INTO Lobby (player_id) VALUES (?)", (player_id,))
        conn.commit()
    finally:
        conn.close()


def remove_from_lobby(player_id):
    """
    Remove a player from the ready lobby.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM Lobby WHERE player_id = ?", (player_id,))
        conn.commit()
    finally:
        conn.close()


def get_lobby_players():
    """
    Get a list of all players currently in the lobby.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT l.player_id, p.username, p.elo, l.joined_at
            FROM Lobby l
            JOIN Player p ON l.player_id = p.player_id
            ORDER BY l.joined_at ASC
        """)
        return [
            {
                "player_id": r[0], 
                "username": r[1], 
                "elo": r[2], 
                "joined_at": r[3]
            } 
            for r in cur.fetchall()
        ]
    finally:
        conn.close()

