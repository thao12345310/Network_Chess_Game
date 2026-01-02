import chess.pgn

def validate_move(fen, move_uci):
    """
    Validate move based on FEN and move in UCI format (e.g., 'e2e4')
    """
    board = chess.Board(fen)
    move = chess.Move.from_uci(move_uci)
    if move in board.legal_moves:
        board.push(move)
        return True, board.fen()
    else:
        return False, fen

def determine_result(fen):
    board = chess.Board(fen)
    if board.is_checkmate():
        return "checkmate"
    elif board.is_stalemate():
        return "draw"
    elif board.is_insufficient_material():
        return "draw"
    elif board.is_seventyfive_moves():
        return "draw"
    else:
        return "in_progress"

def export_pgn(moves, white_name, black_name, result, date, event="Network Chess Game"):
    """
    Generate PGN string from a list of UCI moves.
    """
    game = chess.pgn.Game()
    game.headers["Event"] = event
    game.headers["Site"] = "Local Server"
    game.headers["Date"] = date
    game.headers["Round"] = "1"
    game.headers["White"] = white_name
    game.headers["Black"] = black_name
    game.headers["Result"] = result

    # Replay moves to build the game node tree
    node = game
    board = chess.Board()
    
    for move_uci in moves:
        move = chess.Move.from_uci(move_uci)
        if move in board.legal_moves:
            board.push(move)
            node = node.add_variation(move)
    
    return str(game)


