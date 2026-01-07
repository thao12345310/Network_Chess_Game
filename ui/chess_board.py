#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chess Board Logic and Rendering
"""

import tkinter as tk

try:
    import chess
    HAS_CHESS = True
except ImportError:
    HAS_CHESS = False
    print("WARNING: python-chess not installed. Valid move highlighting disabled.")


class ChessBoard:
    """Chess Board with Tkinter Canvas"""
    
    # Unicode chess pieces
    PIECES = {
        'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔', 'P': '♙',
        'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚', 'p': '♟'
    }
    
    def __init__(self, canvas, square_size=80):
        self.canvas = canvas
        self.square_size = square_size
        self.selected_square = None
        self.highlighted_squares = []  # List of (row, col) for valid moves
        self.board = self.init_board()
        self.current_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        self.is_flipped = False
    
    def set_flipped(self, flipped):
        """Set board orientation (True for Black at bottom)"""
        self.is_flipped = flipped
        self.draw()

    def init_board(self):
        """Initialize chess board"""
        board = [
            ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
            ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
            ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
            ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
        ]
        return board
    
    def reset(self):
        """Reset board to initial position"""
        self.board = self.init_board()
        self.selected_square = None
        self.highlighted_squares = []
        self.current_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        self.is_flipped = False
    
    def draw(self):
        """Draw chess board on canvas"""
        self.canvas.delete("all")
        
        # Draw squares
        for v_row in range(8):
            for v_col in range(8):
                # Calculate logical coordinates
                if self.is_flipped:
                    row, col = 7 - v_row, 7 - v_col
                else:
                    row, col = v_row, v_col
                
                x1 = v_col * self.square_size
                y1 = v_row * self.square_size
                x2 = x1 + self.square_size
                y2 = y1 + self.square_size
                
                # Base color - Check based on logical or visual? 
                # Visual check maintains checkerboard pattern relative to screen.
                # Logical check maintains checkerboard relative to board (h1 is always light).
                # (row+col)%2 == 0 -> Light.
                color = "#F0D9B5" if (row + col) % 2 == 0 else "#B58863"
                
                # Highlight selected square
                if self.selected_square and self.selected_square == (row, col):
                    color = "#BACA44"
                
                # Highlight valid move squares
                is_valid_move = (row, col) in self.highlighted_squares
                if is_valid_move:
                    # Use a different highlight color for valid moves
                    color = "#AED581" if (row + col) % 2 == 0 else "#8BC34A"
                
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="gray")
                
                # Draw valid move indicator (circle)
                if is_valid_move:
                    piece = self.board[row][col]
                    cx = x1 + self.square_size / 2
                    cy = y1 + self.square_size / 2
                    
                    if piece == ' ':
                        # Empty square - draw small dot
                        r = 10
                        self.canvas.create_oval(
                            cx - r, cy - r, cx + r, cy + r,
                            fill="#555555", outline=""
                        )
                    else:
                        # Capturable piece - draw ring around square
                        r = self.square_size / 2 - 5
                        self.canvas.create_oval(
                            cx - r, cy - r, cx + r, cy + r,
                            fill="", outline="#E53935", width=4
                        )
                
                # Draw piece
                piece = self.board[row][col]
                if piece != ' ':
                    piece_symbol = self.PIECES.get(piece, piece)
                    self.canvas.create_text(
                        x1 + self.square_size/2, y1 + self.square_size/2,
                        text=piece_symbol, font=("Arial", 48), fill="black"
                    )
        
        # Draw coordinates
        for i in range(8):
            # Files (a-h)
            label = chr(97 + (7 - i if self.is_flipped else i)) # h..a if flipped, a..h if normal
            self.canvas.create_text(
                i * self.square_size + self.square_size/2, 8 * self.square_size + 15,
                text=label, font=("Arial", 12)
            )
            # Ranks (1-8)
            label = str(i + 1 if self.is_flipped else 8 - i) # 1..8 if flipped, 8..1 if normal
            self.canvas.create_text(
                -15, i * self.square_size + self.square_size/2,
                text=label, font=("Arial", 12)
            )
    
    def get_square_from_coords(self, x, y):
        """Convert canvas coordinates to board square"""
        v_col = x // self.square_size
        v_row = y // self.square_size
        
        if v_row < 0 or v_row > 7 or v_col < 0 or v_col > 7:
            return None
        
        if self.is_flipped:
            return (7 - v_row, 7 - v_col)
        
        return (v_row, v_col)
    
    def pos_to_notation(self, row, col):
        """Convert position to chess notation (e.g., e2)"""
        return f"{chr(97 + col)}{8 - row}"
    
    def notation_to_pos(self, notation):
        """Convert chess notation to position (e.g., e2 -> (6, 4))"""
        if len(notation) < 2:
            return None
        col = ord(notation[0]) - 97
        row = 8 - int(notation[1])
        return (row, col)
    
    def make_move(self, from_row, from_col, to_row, to_col):
        """Move piece on board"""
        self.board[to_row][to_col] = self.board[from_row][from_col]
        self.board[from_row][from_col] = ' '
        self.selected_square = None
        self.highlighted_squares = []  # Clear highlights after move
        
        # Update FEN after move
        if HAS_CHESS:
            try:
                from_notation = self.pos_to_notation(from_row, from_col)
                to_notation = self.pos_to_notation(to_row, to_col)
                board = chess.Board(self.current_fen)
                move = chess.Move.from_uci(from_notation + to_notation)
                if move in board.legal_moves:
                    board.push(move)
                    self.current_fen = board.fen()
            except:
                pass
    
    def get_piece(self, row, col):
        """Get piece at position"""
        if 0 <= row < 8 and 0 <= col < 8:
            return self.board[row][col]
        return None
    
    def get_valid_moves(self, row, col):
        """
        Get list of valid move squares for the piece at (row, col).
        Returns list of (row, col) tuples representing valid destinations.
        """
        if not HAS_CHESS:
            return []
        
        try:
            board = chess.Board(self.current_fen)
            from_square = self.pos_to_notation(row, col)
            from_sq = chess.parse_square(from_square)
            
            valid_moves = []
            for move in board.legal_moves:
                if move.from_square == from_sq:
                    to_notation = chess.square_name(move.to_square)
                    to_pos = self.notation_to_pos(to_notation)
                    if to_pos:
                        valid_moves.append(to_pos)
            
            return valid_moves
        except Exception as e:
            print(f"Error getting valid moves: {e}")
            return []
    
    def set_fen(self, fen):
        """Set the current FEN and update the board display"""
        self.current_fen = fen
        self.update_board_from_fen(fen)
    
    def update_board_from_fen(self, fen):
        """Update the internal board array from a FEN string"""
        if not HAS_CHESS:
            return
        
        try:
            board = chess.Board(fen)
            
            # Clear board
            self.board = [[' ' for _ in range(8)] for _ in range(8)]
            
            # Piece map from python-chess
            piece_map = board.piece_map()
            for square, piece in piece_map.items():
                # chess.square gives us 0-63, need to convert to row, col
                col = square % 8
                row = 7 - (square // 8)  # Flip because chess uses rank 1 at bottom
                
                # Get piece symbol (uppercase=white, lowercase=black)
                symbol = piece.symbol()
                self.board[row][col] = symbol
                
        except Exception as e:
            print(f"Error updating board from FEN: {e}")
    
    def clear_selection(self):
        """Clear the selected square and highlights"""
        self.selected_square = None
        self.highlighted_squares = []
