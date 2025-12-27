#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Game Screen - Màn hình chơi cờ
"""

import tkinter as tk
from tkinter import ttk, messagebox
from chess_board import ChessBoard


class GameScreen:
    """Màn hình chơi game"""
    
    def __init__(self, root, client, on_game_end):
        self.root = root
        self.client = client
        self.on_game_end = on_game_end
        
        # Game state
        self.game_id = None
        self.opponent_name = None
        self.opponent_elo = None
        self.player_color = None
        self.player_elo = None
        
        # Main frame
        self.frame = tk.Frame(root, bg='#ECF0F1')
        
        self.setup_ui()
        self.setup_callbacks()
    
    def setup_ui(self):
        """Setup game UI"""
        # Top bar - Game info
        top_bar = tk.Frame(self.frame, bg='#2C3E50', height=80)
        top_bar.pack(fill='x')
        top_bar.pack_propagate(False)
        
        # Match info
        match_frame = tk.Frame(top_bar, bg='#2C3E50')
        match_frame.pack(expand=True)
        
        # Player info (left)
        self.player_frame = tk.Frame(match_frame, bg='#34495E', relief='raised', bd=2)
        self.player_frame.pack(side='left', padx=20, pady=10)
        
        self.player_name_label = tk.Label(self.player_frame, text="You", 
                                          font=("Arial", 12, "bold"), 
                                          fg='white', bg='#34495E')
        self.player_name_label.pack(padx=20, pady=5)
        
        self.player_elo_label = tk.Label(self.player_frame, text="ELO: 1200", 
                                         font=("Arial", 10), 
                                         fg='#BDC3C7', bg='#34495E')
        self.player_elo_label.pack(padx=20, pady=(0, 5))
        
        # VS label
        tk.Label(match_frame, text="VS", 
                font=("Arial", 20, "bold"), 
                fg='#E74C3C', bg='#2C3E50').pack(side='left', padx=30)
        
        # Opponent info (right)
        self.opponent_frame = tk.Frame(match_frame, bg='#34495E', relief='raised', bd=2)
        self.opponent_frame.pack(side='left', padx=20, pady=10)
        
        self.opponent_name_label = tk.Label(self.opponent_frame, text="Opponent", 
                                           font=("Arial", 12, "bold"), 
                                           fg='white', bg='#34495E')
        self.opponent_name_label.pack(padx=20, pady=5)
        
        self.opponent_elo_label = tk.Label(self.opponent_frame, text="ELO: 1200", 
                                          font=("Arial", 10), 
                                          fg='#BDC3C7', bg='#34495E')
        self.opponent_elo_label.pack(padx=20, pady=(0, 5))
        
        # Main game area
        game_area = tk.Frame(self.frame, bg='#ECF0F1')
        game_area.pack(fill='both', expand=True, pady=20)
        
        # Left panel - Game status
        left_panel = tk.Frame(game_area, bg='white', width=250, relief='solid', bd=1)
        left_panel.pack(side='left', fill='y', padx=(20, 10))
        left_panel.pack_propagate(False)
        
        tk.Label(left_panel, text="Game Status", 
                font=("Arial", 14, "bold"), 
                fg='#2C3E50', bg='white').pack(pady=15)
        
        # Turn indicator
        self.turn_label = tk.Label(left_panel, text="Your turn", 
                                   font=("Arial", 12), 
                                   fg='#27AE60', bg='white')
        self.turn_label.pack(pady=10)
        
        # Your color
        self.color_frame = tk.Frame(left_panel, bg='white')
        self.color_frame.pack(pady=15)
        
        tk.Label(self.color_frame, text="You are playing:", 
                font=("Arial", 10), 
                fg='#7F8C8D', bg='white').pack()
        
        self.color_label = tk.Label(self.color_frame, text="⚪ White", 
                                    font=("Arial", 14, "bold"), 
                                    fg='#2C3E50', bg='white')
        self.color_label.pack(pady=5)
        
        ttk.Separator(left_panel, orient='horizontal').pack(fill='x', 
                                                            padx=20, pady=15)
        
        # Move history
        tk.Label(left_panel, text="Move History", 
                font=("Arial", 11, "bold"), 
                fg='#2C3E50', bg='white').pack()
        
        self.moves_text = tk.Text(left_panel, width=25, height=15, 
                                 font=("Courier New", 9),
                                 relief='flat', bg='#F8F9FA')
        self.moves_text.pack(pady=10, padx=10)
        self.moves_text.config(state='disabled')
        
        # Center - Chess board
        board_container = tk.Frame(game_area, bg='#ECF0F1')
        board_container.pack(side='left', padx=20)
        
        # Game title
        self.game_title = tk.Label(board_container, text="Chess Game", 
                                   font=("Arial", 16, "bold"), 
                                   fg='#2C3E50', bg='#ECF0F1')
        self.game_title.pack(pady=10)
        
        # Chess board canvas
        self.board_canvas = tk.Canvas(board_container, width=640, height=640, 
                                     bg='white', relief='solid', bd=2)
        self.board_canvas.pack()
        self.board_canvas.bind("<Button-1>", self.on_square_click)
        
        # Initialize chess board
        self.chess_board = ChessBoard(self.board_canvas, square_size=80)
        self.chess_board.draw()
        
        # Control buttons
        control_frame = tk.Frame(board_container, bg='#ECF0F1')
        control_frame.pack(pady=15)
        
        tk.Button(control_frame, text="🏳️ Resign", 
                 command=self.do_resign,
                 bg='#E74C3C', fg='white', 
                 font=("Arial", 11, "bold"),
                 relief='flat', cursor='hand2',
                 width=12).pack(side='left', padx=5, ipady=8)
        
        tk.Button(control_frame, text="🤝 Offer Draw", 
                 command=self.offer_draw,
                 bg='#F39C12', fg='white', 
                 font=("Arial", 11, "bold"),
                 relief='flat', cursor='hand2',
                 width=12).pack(side='left', padx=5, ipady=8)
        
        tk.Button(control_frame, text="💬 Chat", 
                 command=self.open_chat,
                 bg='#3498DB', fg='white', 
                 font=("Arial", 11, "bold"),
                 relief='flat', cursor='hand2',
                 width=12).pack(side='left', padx=5, ipady=8)
        
        # Right panel - captured pieces and info
        right_panel = tk.Frame(game_area, bg='white', width=250, relief='solid', bd=1)
        right_panel.pack(side='left', fill='y', padx=(10, 20))
        right_panel.pack_propagate(False)
        
        tk.Label(right_panel, text="Captured Pieces", 
                font=("Arial", 12, "bold"), 
                fg='#2C3E50', bg='white').pack(pady=15)
        
        # Opponent captures
        tk.Label(right_panel, text="Opponent captured:", 
                font=("Arial", 9), 
                fg='#7F8C8D', bg='white').pack()
        
        self.opp_captures = tk.Label(right_panel, text="", 
                                     font=("Arial", 20), 
                                     fg='#2C3E50', bg='white')
        self.opp_captures.pack(pady=10)
        
        ttk.Separator(right_panel, orient='horizontal').pack(fill='x', 
                                                             padx=20, pady=10)
        
        # Your captures
        tk.Label(right_panel, text="You captured:", 
                font=("Arial", 9), 
                fg='#7F8C8D', bg='white').pack()
        
        self.your_captures = tk.Label(right_panel, text="", 
                                      font=("Arial", 20), 
                                      fg='#2C3E50', bg='white')
        self.your_captures.pack(pady=10)
    
    def setup_callbacks(self):
        """Setup network callbacks"""
        self.client.set_callback('MOVE_RESPONSE', self.on_move_response)
        self.client.set_callback('GAME_UPDATE', self.on_game_update)
        self.client.set_callback('GAME_END', self.on_game_end_msg)
    
    def start_game(self, game_id, opponent, your_color, opponent_elo, player_elo):
        """Initialize game with data"""
        self.game_id = game_id
        self.opponent_name = opponent
        self.player_color = your_color
        self.opponent_elo = opponent_elo
        self.player_elo = player_elo
        
        # Update UI
        self.player_name_label.config(text=f"👤 {self.client.username}")
        self.player_elo_label.config(text=f"⭐ ELO: {player_elo}")
        
        self.opponent_name_label.config(text=f"👤 {opponent}")
        self.opponent_elo_label.config(text=f"⭐ ELO: {opponent_elo}")
        
        color_emoji = "⚪ White" if your_color == 'white' else "⚫ Black"
        self.color_label.config(text=color_emoji)
        
        self.game_title.config(text=f"Game vs {opponent}")
        
        # Reset board
        self.chess_board.reset()
        self.chess_board.draw()
        
        # Clear moves
        self.moves_text.config(state='normal')
        self.moves_text.delete('1.0', 'end')
        self.moves_text.config(state='disabled')
    
    def on_square_click(self, event):
        """Handle board square click"""
        square = self.chess_board.get_square_from_coords(event.x, event.y)
        if not square:
            return
        
        row, col = square
        
        if self.chess_board.selected_square is None:
            # Select piece
            piece = self.chess_board.get_piece(row, col)
            if piece and piece != ' ':
                self.chess_board.selected_square = (row, col)
        else:
            # Make move
            from_row, from_col = self.chess_board.selected_square
            from_pos = self.chess_board.pos_to_notation(from_row, from_col)
            to_pos = self.chess_board.pos_to_notation(row, col)
            
            # Update local board
            self.chess_board.make_move(from_row, from_col, row, col)
            
            # Send to server
            if self.client.connected and self.game_id:
                self.client.make_move(self.game_id, from_pos, to_pos)
                self.add_move(from_pos, to_pos)
        
        self.chess_board.draw()
    
    def add_move(self, from_pos, to_pos):
        """Add move to history"""
        self.moves_text.config(state='normal')
        self.moves_text.insert('end', f"{from_pos} → {to_pos}\n")
        self.moves_text.see('end')
        self.moves_text.config(state='disabled')
    
    def do_resign(self):
        """Resign from game"""
        result = messagebox.askyesno("Resign", 
                                     "Are you sure you want to resign?\nYou will lose ELO points.")
        if result:
            self.client.resign(self.game_id)
    
    def offer_draw(self):
        """Offer draw"""
        self.client.offer_draw(self.game_id)
        messagebox.showinfo("Draw Offer", "Draw offer sent to opponent")
    
    def open_chat(self):
        """Open chat (placeholder)"""
        messagebox.showinfo("Chat", "Chat feature coming soon!")
    
    def on_move_response(self, msg):
        """Handle move response"""
        if not msg.get('success'):
            error = msg.get('message', 'Invalid move')
            messagebox.showerror("Invalid Move", error)
            # Revert board
            self.chess_board.reset()
            self.chess_board.draw()
    
    def on_game_update(self, msg):
        """Handle game update"""
        move = msg.get('last_move')
        if move:
            # Opponent's move
            self.add_move(move.get('from', '?'), move.get('to', '?'))
            # TODO: Update board from server state
    
    def on_game_end_msg(self, msg):
        """Handle game end"""
        winner = msg.get('winner')
        reason = msg.get('reason', 'Game ended')
        elo_change = msg.get('elo_change', 0)
        new_elo = msg.get('new_elo', self.player_elo)
        
        if winner == self.client.username:
            result_text = f"🎉 You Won! 🎉\n\n{reason}\n\nELO: {self.player_elo} → {new_elo} (+{elo_change})"
        elif winner == 'draw':
            result_text = f"🤝 Draw\n\n{reason}\n\nELO: {self.player_elo} → {new_elo}"
        else:
            result_text = f"😞 You Lost\n\n{reason}\n\nELO: {self.player_elo} → {new_elo} ({elo_change})"
        
        messagebox.showinfo("Game Over", result_text)
        
        self.hide()
        self.on_game_end(new_elo)
    
    def show(self):
        """Show game screen"""
        self.frame.pack(fill='both', expand=True)
    
    def hide(self):
        """Hide game screen"""
        self.frame.pack_forget()
