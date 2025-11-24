import datetime

from database import get_connection
from init_db import init_db
from game_logic import validate_move
from db_handler import insert_move, get_moves


INITIAL_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"


def create_test_players_and_game():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO Player (username, password, elo) VALUES (?, ?, ?)",
        ("alice", "pass", 1200),
    )
    white_id = cur.lastrowid

    cur.execute(
        "INSERT INTO Player (username, password, elo) VALUES (?, ?, ?)",
        ("bob", "pass", 1200),
    )
    black_id = cur.lastrowid

    cur.execute(
        "INSERT INTO Game (white_id, black_id, mode, start_time, status) VALUES (?, ?, ?, ?, ?)",
        (
            white_id,
            black_id,
            "CLASSICAL",
            datetime.datetime.utcnow().isoformat(),
            "ONGOING",
        ),
    )
    game_id = cur.lastrowid

    conn.commit()
    conn.close()

    return white_id, black_id, game_id


def main():
    init_db()

    white_id, black_id, game_id = create_test_players_and_game()

    # test a legal move from the initial position
    move = "e2e4"
    ok, next_fen = validate_move(INITIAL_FEN, move)
    print(f"Validate {move}: {ok}")

    if ok:
        insert_move(game_id=game_id, player_id=white_id, move_notation=move)
        moves = get_moves(game_id)
        print("Moves in DB:", moves)
        print("Next FEN:", next_fen)
    else:
        print("Move invalid; nothing inserted.")


if __name__ == "__main__":
    main()
