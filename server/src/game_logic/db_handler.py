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


def get_current_player_turn(game_id):
    """
    Get player_id of the player whose turn it is to move.
    Based on FEN turn indicator (w = white, b = black).
    Returns None if game not found.
    """
    fen = get_game_fen(game_id)
    
    # Parse FEN to get turn: "rnbqkbnr/... w ..." or "rnbqkbnr/... b ..."
    parts = fen.split()
    if len(parts) < 2:
        return None
    
    turn_char = parts[1]  # 'w' or 'b'
    
    # Get white_id and black_id from Game table
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT white_id, black_id FROM Game WHERE game_id = ?",
        (game_id,)
    )
    result = cur.fetchone()
    conn.close()
    
    if not result:
        return None
    
    white_id, black_id = result
    
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
