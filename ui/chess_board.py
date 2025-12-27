#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chess Board Logic and Rendering
"""

import tkinter as tk


class ChessBoard:
    """Chess Board with Tkinter Canvas"""
    
    # Unicode chess pieces
    PIECES = {
        'R': '♜', 'N': '♞', 'B': '♝', 'Q': '♛', 'K': '♚', 'P': '♟',
        'r': '♖', 'n': '♘', 'b': '♗', 'q': '♕', 'k': '♔', 'p': '♙'
    }
    
    def __init__(self, canvas, square_size=80):
        self.canvas = canvas
        self.square_size = square_size
        self.selected_square = None
        self.board = self.init_board()
    
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
    
    def draw(self):
        """Draw chess board on canvas"""
        self.canvas.delete("all")
        
        # Draw squares
        for row in range(8):
            for col in range(8):
                x1 = col * self.square_size
                y1 = row * self.square_size
                x2 = x1 + self.square_size
                y2 = y1 + self.square_size
                
                # Color
                color = "#F0D9B5" if (row + col) % 2 == 0 else "#B58863"
                
                # Highlight selected
                if self.selected_square and self.selected_square == (row, col):
                    color = "#BACA44"
                
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="gray")
                
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
            self.canvas.create_text(
                i * self.square_size + self.square_size/2, 8 * self.square_size + 15,
                text=chr(97 + i), font=("Arial", 12)
            )
            # Ranks (1-8)
            self.canvas.create_text(
                -15, i * self.square_size + self.square_size/2,
                text=str(8 - i), font=("Arial", 12)
            )
    
    def get_square_from_coords(self, x, y):
        """Convert canvas coordinates to board square"""
        col = x // self.square_size
        row = y // self.square_size
        
        if row < 0 or row > 7 or col < 0 or col > 7:
            return None
        
        return (row, col)
    
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
    
    def get_piece(self, row, col):
        """Get piece at position"""
        if 0 <= row < 8 and 0 <= col < 8:
            return self.board[row][col]
        return None
