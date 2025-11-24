import sqlite3
from database import get_connection


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
