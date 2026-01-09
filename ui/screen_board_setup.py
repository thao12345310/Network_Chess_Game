#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Custom Board Setup Screen - Tự setup vị trí quân cờ để chơi với chính mình
"""

import tkinter as tk
from tkinter import ttk, messagebox
import chess


class BoardSetupScreen:
    """Màn hình setup custom board position"""
    
    def __init__(self, root, on_start_practice, on_back, appearance_settings=None):
        self.root = root
        self.on_start_practice = on_start_practice
        self.on_back = on_back
        self.appearance_settings = appearance_settings
        
        # Setup board state
        self.board = chess.Board()
        self.board.clear()  # Bắt đầu với bàn cờ trống
        self.selected_piece = None
        self.turn = chess.WHITE  # Người chơi nào đi trước
        
        # UI state
        self.selected_square = None
        self.square_size = 70
        
        # Piece symbols
        self.piece_symbols = {
            'white': ['P', 'N', 'B', 'R', 'Q', 'K'],
            'black': ['p', 'n', 'b', 'r', 'q', 'k']
        }
        
        self.frame = tk.Frame(root, bg='#ECF0F1')
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI cho màn hình board setup"""
        # Top bar
        top_bar = tk.Frame(self.frame, bg='#2C3E50', height=60)
        top_bar.pack(fill='x')
        top_bar.pack_propagate(False)
        
        tk.Label(top_bar, text="♟ Custom Board Setup", 
                font=("Arial", 18, "bold"), 
                fg='#ECF0F1', bg='#2C3E50').pack(side='left', padx=20)
        
        tk.Button(top_bar, text="← Back", 
                 command=self.on_back,
                 bg='#95A5A6', fg='white',
                 font=("Arial", 10, "bold"),
                 relief='flat', cursor='hand2',
                 padx=15, pady=5).pack(side='right', padx=20)
        
        # Main content
        content = tk.Frame(self.frame, bg='#ECF0F1')
        content.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Left panel - Piece palette
        left_panel = tk.Frame(content, bg='white', relief='solid', bd=1)
        left_panel.pack(side='left', fill='y', padx=(0, 10))
        
        tk.Label(left_panel, text="Select Piece", 
                font=("Arial", 12, "bold"),
                fg='#2C3E50', bg='white').pack(pady=10, padx=10)
        
        # White pieces
        tk.Label(left_panel, text="White Pieces", 
                font=("Arial", 10, "bold"),
                fg='#34495E', bg='white').pack(pady=(5,0), padx=10, anchor='w')
        
        white_frame = tk.Frame(left_panel, bg='white')
        white_frame.pack(pady=5, padx=10)
        
        piece_display = {'P': '♙', 'N': '♘', 'B': '♗', 'R': '♖', 'Q': '♕', 'K': '♔',
                         'p': '♟', 'n': '♞', 'b': '♝', 'r': '♜', 'q': '♛', 'k': '♚'}
        
        for piece in self.piece_symbols['white']:
            def make_command(p):
                return lambda: self.select_piece(p)
            
            btn = tk.Button(white_frame, text=piece_display[piece],
                          font=("Arial", 24),
                          width=2, height=1,
                          bg='#ECF0F1',
                          relief='raised',
                          cursor='hand2',
                          command=make_command(piece))
            btn.pack(pady=2)
        
        # Black pieces
        tk.Label(left_panel, text="Black Pieces", 
                font=("Arial", 10, "bold"),
                fg='#34495E', bg='white').pack(pady=(15,0), padx=10, anchor='w')
        
        black_frame = tk.Frame(left_panel, bg='white')
        black_frame.pack(pady=5, padx=10)
        
        for piece in self.piece_symbols['black']:
            def make_command(p):
                return lambda: self.select_piece(p)
            
            btn = tk.Button(black_frame, text=piece_display[piece],
                          font=("Arial", 24),
                          width=2, height=1,
                          bg='#ECF0F1',
                          relief='raised',
                          cursor='hand2',
                          command=make_command(piece))
            btn.pack(pady=2)
        
        ttk.Separator(left_panel, orient='horizontal').pack(fill='x', pady=10)
        
        # Reset to standard
        tk.Button(left_panel, text="Standard Position",
                 font=("Arial", 10, "bold"),
                 bg='#27AE60', fg='white',
                 relief='flat', cursor='hand2',
                 command=self.reset_standard,
                 padx=10, pady=5).pack(pady=5, padx=10)
        
        # Center panel - Chess board
        center_panel = tk.Frame(content, bg='white', relief='solid', bd=1)
        center_panel.pack(side='left', padx=10)
        
        # Board canvas
        board_size = self.square_size * 8
        self.canvas = tk.Canvas(center_panel, width=board_size, height=board_size,
                               bg='white', highlightthickness=0)
        self.canvas.pack(padx=10, pady=10)
        self.canvas.bind('<Button-1>', self.on_square_click)
        
        # Right panel - Controls
        right_panel = tk.Frame(content, bg='white', relief='solid', bd=1)
        right_panel.pack(side='left', fill='y', padx=(10, 0))
        
        tk.Label(right_panel, text="Game Settings", 
                font=("Arial", 12, "bold"),
                fg='#2C3E50', bg='white').pack(pady=15, padx=20)
        
        # Turn to move
        turn_frame = tk.Frame(right_panel, bg='white')
        turn_frame.pack(pady=10, padx=20, fill='x')
        
        tk.Label(turn_frame, text="Turn to move:", 
                font=("Arial", 10, "bold"),
                fg='#34495E', bg='white').pack(anchor='w')
        
        self.turn_var = tk.StringVar(value="white")
        tk.Radiobutton(turn_frame, text="White",
                      variable=self.turn_var, value="white",
                      font=("Arial", 10),
                      bg='white',
                      activebackground='white',
                      selectcolor='#ECF0F1',
                      cursor='hand2',
                      command=self.update_turn).pack(anchor='w', pady=2)
        
        tk.Radiobutton(turn_frame, text="Black",
                      variable=self.turn_var, value="black",
                      font=("Arial", 10),
                      bg='white',
                      activebackground='white',
                      selectcolor='#ECF0F1',
                      cursor='hand2',
                      command=self.update_turn).pack(anchor='w', pady=2)
        
        ttk.Separator(right_panel, orient='horizontal').pack(fill='x', pady=15)
        
        # FEN display
        fen_frame = tk.Frame(right_panel, bg='white')
        fen_frame.pack(pady=10, padx=20, fill='x')
        
        tk.Label(fen_frame, text="FEN Position:", 
                font=("Arial", 10, "bold"),
                fg='#34495E', bg='white').pack(anchor='w')
        
        self.fen_text = tk.Text(fen_frame, height=4, width=25,
                               font=("Courier", 8),
                               wrap='word', relief='solid', bd=1)
        self.fen_text.pack(pady=5)
        
        tk.Button(fen_frame, text="Copy FEN",
                 font=("Arial", 9),
                 bg='#95A5A6', fg='white',
                 relief='flat', cursor='hand2',
                 command=self.copy_fen,
                 padx=8, pady=3).pack()
        
        ttk.Separator(right_panel, orient='horizontal').pack(fill='x', pady=15)
        
        # Board actions
        tk.Label(right_panel, text="Board Actions", 
                font=("Arial", 10, "bold"),
                fg='#34495E', bg='white').pack(pady=(5,10), padx=20)
        
        # Eraser button
        tk.Button(right_panel, text="🗑️ Eraser",
                 font=("Arial", 10, "bold"),
                 bg='#E74C3C', fg='white',
                 relief='flat', cursor='hand2',
                 command=lambda: self.select_piece(None),
                 width=18, pady=5).pack(pady=5, padx=20)
        
        # Clear board button
        tk.Button(right_panel, text="Clear Board",
                 font=("Arial", 10, "bold"),
                 bg='#E67E22', fg='white',
                 relief='flat', cursor='hand2',
                 command=self.clear_board,
                 width=18, pady=5).pack(pady=5, padx=20)
        
        ttk.Separator(right_panel, orient='horizontal').pack(fill='x', pady=15)
        
        # Validation status
        self.status_label = tk.Label(right_panel, text="",
                                     font=("Arial", 9),
                                     fg='#E74C3C', bg='white',
                                     wraplength=180)
        self.status_label.pack(pady=10, padx=20)
        
        # Start practice button
        self.start_btn = tk.Button(right_panel, text="▶ Start Practice",
                                   font=("Arial", 12, "bold"),
                                   bg='#27AE60', fg='white',
                                   relief='flat', cursor='hand2',
                                   command=self.start_practice,
                                   padx=15, pady=10)
        self.start_btn.pack(pady=20, padx=20)
        
        # Initial draw
        self.draw_board()
        self.update_fen_display()
    
    def select_piece(self, piece):
        """Select piece for placing on board"""
        self.selected_piece = piece
        # Visual feedback không cần thiết nhưng có thể thêm sau
    
    def on_square_click(self, event):
        """Handle click on board square"""
        col = event.x // self.square_size
        row = event.y // self.square_size
        
        if 0 <= row < 8 and 0 <= col < 8:
            square = chess.square(col, 7 - row)  # chess library dùng 0-63 from bottom-left
            
            if self.selected_piece is None:
                # Eraser mode - remove piece
                self.board.remove_piece_at(square)
            else:
                # Place piece
                piece_type_map = {
                    'P': chess.PAWN, 'N': chess.KNIGHT, 'B': chess.BISHOP,
                    'R': chess.ROOK, 'Q': chess.QUEEN, 'K': chess.KING,
                    'p': chess.PAWN, 'n': chess.KNIGHT, 'b': chess.BISHOP,
                    'r': chess.ROOK, 'q': chess.QUEEN, 'k': chess.KING
                }
                
                piece_type = piece_type_map[self.selected_piece]
                color = chess.WHITE if self.selected_piece.isupper() else chess.BLACK
                
                piece = chess.Piece(piece_type, color)
                self.board.set_piece_at(square, piece)
            
            self.draw_board()
            self.update_fen_display()
            self.validate_position()
    
    def draw_board(self):
        """Draw the chess board with current pieces"""
        self.canvas.delete("all")
        
        # Colors
        light_color = '#F0D9B5'
        dark_color = '#B58863'
        
        # Draw squares
        for row in range(8):
            for col in range(8):
                x1 = col * self.square_size
                y1 = row * self.square_size
                x2 = x1 + self.square_size
                y2 = y1 + self.square_size
                
                color = light_color if (row + col) % 2 == 0 else dark_color
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline='')
        
        # Draw pieces
        piece_display = {
            'P': '♙', 'N': '♘', 'B': '♗', 'R': '♖', 'Q': '♕', 'K': '♔',
            'p': '♟', 'n': '♞', 'b': '♝', 'r': '♜', 'q': '♛', 'k': '♚'
        }
        
        for row in range(8):
            for col in range(8):
                square = chess.square(col, 7 - row)
                piece = self.board.piece_at(square)
                
                if piece:
                    piece_char = piece.symbol()
                    x = col * self.square_size + self.square_size // 2
                    y = row * self.square_size + self.square_size // 2
                    
                    # Màu khác nhau cho quân trắng và đen
                    piece_color = 'white' if piece.color == chess.WHITE else '#2C3E50'
                    
                    self.canvas.create_text(x, y,
                                          text=piece_display[piece_char],
                                          font=("Arial", 48),
                                          fill=piece_color)
    
    def update_fen_display(self):
        """Update FEN text display"""
        try:
            # Build FEN manually since board may not be valid
            fen_parts = []
            
            # Board position
            for rank in range(7, -1, -1):
                empty_count = 0
                rank_str = ""
                for file in range(8):
                    square = chess.square(file, rank)
                    piece = self.board.piece_at(square)
                    if piece:
                        if empty_count > 0:
                            rank_str += str(empty_count)
                            empty_count = 0
                        rank_str += piece.symbol()
                    else:
                        empty_count += 1
                
                if empty_count > 0:
                    rank_str += str(empty_count)
                fen_parts.append(rank_str)
            
            board_fen = "/".join(fen_parts)
            
            # Turn
            turn_char = 'w' if self.turn == chess.WHITE else 'b'
            
            # Castling rights - default to all available for setup
            castling = 'KQkq'
            
            # En passant - none for setup
            en_passant = '-'
            
            # Halfmove and fullmove
            halfmove = '0'
            fullmove = '1'
            
            fen = f"{board_fen} {turn_char} {castling} {en_passant} {halfmove} {fullmove}"
            
            self.fen_text.delete('1.0', 'end')
            self.fen_text.insert('1.0', fen)
        except Exception as e:
            self.fen_text.delete('1.0', 'end')
            self.fen_text.insert('1.0', f"Error: {str(e)}")
    
    def update_turn(self):
        """Update turn to move"""
        self.turn = chess.WHITE if self.turn_var.get() == "white" else chess.BLACK
        self.update_fen_display()
        self.validate_position()
    
    def validate_position(self):
        """Validate the current board position"""
        try:
            # Check for required kings
            white_kings = len(self.board.pieces(chess.KING, chess.WHITE))
            black_kings = len(self.board.pieces(chess.KING, chess.BLACK))
            
            errors = []
            
            if white_kings == 0:
                errors.append("Missing White King")
            elif white_kings > 1:
                errors.append("Multiple White Kings")
            
            if black_kings == 0:
                errors.append("Missing Black King")
            elif black_kings > 1:
                errors.append("Multiple Black Kings")
            
            # Check for pawns on first/last rank
            for square in chess.SQUARES:
                rank = chess.square_rank(square)
                piece = self.board.piece_at(square)
                if piece and piece.piece_type == chess.PAWN:
                    if rank == 0 or rank == 7:
                        errors.append("Pawns on first/last rank")
                        break
            
            if errors:
                self.status_label.config(text="⚠ " + ", ".join(errors), fg='#E74C3C')
                self.start_btn.config(state='disabled', bg='#95A5A6')
                return False
            else:
                self.status_label.config(text="✓ Valid position", fg='#27AE60')
                self.start_btn.config(state='normal', bg='#27AE60')
                return True
        except Exception as e:
            self.status_label.config(text=f"⚠ Error: {str(e)}", fg='#E74C3C')
            self.start_btn.config(state='disabled', bg='#95A5A6')
            return False
    
    def clear_board(self):
        """Clear all pieces from board"""
        self.board.clear()
        self.draw_board()
        self.update_fen_display()
        self.validate_position()
    
    def reset_standard(self):
        """Reset to standard starting position"""
        self.board.reset()
        self.turn = chess.WHITE
        self.turn_var.set("white")
        self.draw_board()
        self.update_fen_display()
        self.validate_position()
    
    def copy_fen(self):
        """Copy FEN to clipboard"""
        fen = self.fen_text.get('1.0', 'end-1c')
        self.root.clipboard_clear()
        self.root.clipboard_append(fen)
        messagebox.showinfo("Copied", "FEN copied to clipboard!")
    
    def start_practice(self):
        """Start practice mode with current board setup"""
        if not self.validate_position():
            messagebox.showerror("Invalid Position", 
                               "Please fix the errors before starting practice mode.")
            return
        
        fen = self.fen_text.get('1.0', 'end-1c')
        self.on_start_practice(fen)
    
    def show(self):
        """Show this screen"""
        self.frame.pack(fill='both', expand=True)
    
    def hide(self):
        """Hide this screen"""
        self.frame.pack_forget()


if __name__ == "__main__":
    # Test the screen
    root = tk.Tk()
    root.title("Board Setup Test")
    root.geometry("1300x750")
    
    def on_start(fen):
        print(f"Starting practice with FEN: {fen}")
    
    def on_back():
        print("Back pressed")
        root.quit()
    
    screen = BoardSetupScreen(root, on_start, on_back)
    screen.show()
    
    root.mainloop()
