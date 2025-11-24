import chess

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

