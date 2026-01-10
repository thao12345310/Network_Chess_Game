#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Game Screen - Màn hình chơi cờ
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from chess_board import ChessBoard
from protocol_constants import MessageType, ResponseCode, PayloadFields
import time


class GameScreen:
    """Màn hình chơi game"""
    
    def __init__(self, root, client, on_game_end, appearance_settings=None):
        self.root = root
        self.client = client
        self.on_game_end = on_game_end
        self.appearance_settings = appearance_settings
        
        # Game state
        self.game_id = None
        self.opponent_name = None
        self.player_elo = None
        self.time_control_seconds = None
        self.last_move_time = None
        self.white_time_left = None
        self.black_time_left = None
        self.is_game_active = False
        self.last_claim_time = 0
        self.timer_delay_offset = 0 # Offset for initial startup delay
        self.is_practice_mode = False  # Practice mode flag
        
        # Store original MATCH_START callback from Lobby (to restore later)
        self.lobby_match_start_callback = None
        
        # Track active rematch dialog to close it when opponent requests
        self.active_rematch_dialog = None
        
        # Main frame
        self.frame = tk.Frame(root, bg='#ECF0F1')
        
        self.setup_ui()
        self.setup_callbacks()
    
    def setup_ui(self):
        """Setup game UI"""
        # Top bar - Game info
        top_bar = tk.Frame(self.frame, bg='#2C3E50', height=120)
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
        
        self.player_time_label = tk.Label(self.player_frame, text="10:00",
                                          font=("Arial", 16, "bold"),
                                          fg='#2ECC71', bg='#34495E')
        self.player_time_label.pack(padx=20, pady=(5, 10))
        
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
        
        self.opponent_time_label = tk.Label(self.opponent_frame, text="10:00",
                                            font=("Arial", 16, "bold"),
                                            fg='#F39C12', bg='#34495E')
        self.opponent_time_label.pack(padx=20, pady=(5, 10))
        
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
        
        # Initialize chess board with appearance settings
        self.chess_board = ChessBoard(self.board_canvas, square_size=80, 
                                      appearance_settings=self.appearance_settings)
        self.chess_board.draw()
        
        # Control buttons
        control_frame = tk.Frame(board_container, bg='#ECF0F1')
        control_frame.pack(pady=15)
        
        # Store button references to hide/show based on game mode
        self.resign_btn = tk.Button(control_frame, text="🏳️ Resign", 
                 command=self.do_resign,
                 bg='#E74C3C', fg='white', 
                 font=("Arial", 11, "bold"),
                 relief='flat', cursor='hand2',
                 width=12)
        self.resign_btn.pack(side='left', padx=5, ipady=8)
        
        self.draw_btn = tk.Button(control_frame, text="🤝 Offer Draw", 
                 command=self.offer_draw,
                 bg='#F39C12', fg='white', 
                 font=("Arial", 11, "bold"),
                 relief='flat', cursor='hand2',
                 width=12)
        self.draw_btn.pack(side='left', padx=5, ipady=8)
        
        # Back button for practice mode
        self.back_btn = tk.Button(control_frame, text="← Back to Lobby", 
                 command=self.return_to_lobby,
                 bg='#95A5A6', fg='white', 
                 font=("Arial", 11, "bold"),
                 relief='flat', cursor='hand2',
                 width=15)
        # Will be shown/hidden based on game mode
        
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
        self.client.set_callback(MessageType.MOVE_ACK, self.on_move_response)
        self.client.set_callback(MessageType.MOVE_UPDATE, self.on_game_update)
        self.client.set_callback(MessageType.EMOJI_UPDATE, self.on_emoji_update)
        self.client.set_callback(MessageType.GAME_END, self.on_game_end_msg)
        self.client.set_callback(MessageType.DRAW_OFFER_NOTIFY, self.on_draw_offer_received)
        self.client.set_callback(MessageType.REMATCH_REQUEST_NOTIFY, self.on_rematch_request_received)
        self.client.set_callback(MessageType.REMATCH_DECLINED_NOTIFY, self.on_rematch_declined)
        # NOTE: DO NOT register MATCH_START here - it will override Lobby's callback
        # MATCH_START for rematch is registered dynamically when needed
    
    def check_connection(self):
        """Check if still connected to server"""
        if not self.is_practice_mode and not self.client.connected:
            # Connection lost during game
            self.is_game_active = False
            return False
        return True
    
    def start_game(self, game_id, opponent, your_color, opponent_elo, player_elo, time_control="10+0", is_rematch=False, custom_fen=None):
        """Initialize game with data"""
        print(f"DEBUG: start_game called. Game: {game_id}, Me: {self.client.username}, Color: '{your_color}', TC: {time_control}, Rematch: {is_rematch}, Custom FEN: {custom_fen}")
        self.game_id = game_id
        self.opponent_name = opponent
        self.player_color = your_color
        self.opponent_elo = opponent_elo
        self.player_elo = player_elo
        
        # Practice mode: game_id is None and opponent is "Practice Mode"
        self.is_practice_mode = (game_id is None and opponent == "Practice Mode")
        print(f"DEBUG: Practice mode: {self.is_practice_mode}")
        
        # Only register MATCH_START callback on first game start (not rematch)
        if not is_rematch:
            # Save Lobby's MATCH_START callback before overriding it
            if MessageType.MATCH_START in self.client.callbacks and self.lobby_match_start_callback is None:
                self.lobby_match_start_callback = self.client.callbacks[MessageType.MATCH_START]
                print("DEBUG: Saved Lobby's MATCH_START callback")
            
            # Register our MATCH_START callback now (for rematch)
            self.client.set_callback(MessageType.MATCH_START, self.on_match_start)
            print("DEBUG: Registered GameScreen's MATCH_START callback")
        else:
            print("DEBUG: Rematch - callback already registered, skipping")
        
        # Update UI
        self.player_name_label.config(text=f"👤 {self.client.username}")
        self.player_elo_label.config(text=f"⭐ ELO: {player_elo}")
        
        self.opponent_name_label.config(text=f"👤 {opponent}")
        self.opponent_elo_label.config(text=f"⭐ ELO: {opponent_elo}")
        
        # Parse time control (format "10+0" -> 10 mins)
        try:
            minutes = int(time_control.split('+')[0])
            self.time_control_seconds = minutes * 60.0
            time_str = f"{minutes:02d}:00"
        except:
            self.time_control_seconds = 600.0
            time_str = "10:00"
            
        self.white_time_left = self.time_control_seconds
        self.black_time_left = self.time_control_seconds
        # Timer starts immediately on game start (matching server logic)
        self.last_move_time = time.time()
        
        # Add 4s delay for initial startup stability
        self.timer_delay_offset = 2.0

        
        self.player_time_label.config(text=time_str)
        self.opponent_time_label.config(text=time_str)
        
        self.is_game_active = True
        self.check_timeout() # Start background checker
        
        color_emoji = "⚪ White" if your_color == 'white' else "⚫ Black"
        self.color_label.config(text=color_emoji)
        
        self.game_title.config(text=f"Game vs {opponent}")
        
        
       # Reset board or load custom FEN
        if custom_fen:
            # Load custom position from FEN
            self.chess_board.load_fen(custom_fen)
            print(f"DEBUG: Loaded custom FEN: {custom_fen}")
        else:
            # Standard starting position
            self.chess_board.reset()
        
        self.chess_board.draw()
        
        # Set initial turn label based on FEN (if custom) or standard
        if custom_fen:
            # Parse FEN to determine whose turn it is
            fen_parts = custom_fen.split()
            if len(fen_parts) >= 2:
                turn_char = fen_parts[1]  # 'w' or 'b'
                is_your_turn = (turn_char == 'w' and self.player_color == 'white') or \
                               (turn_char == 'b' and self.player_color == 'black')
            else:
                is_your_turn = (self.player_color == 'white')
        else:
            # Standard chess: White always moves first
            is_your_turn = (self.player_color == 'white')
        
        print(f"DEBUG: Initial turn check. Me: {self.player_color}. My turn? {is_your_turn}")
        
        if is_your_turn:
            self.turn_label.config(text="Your turn", fg='#27AE60')
        else:
            self.turn_label.config(text="Opponent's turn", fg='#E74C3C')
        
        # Flip board if playing Black
        self.chess_board.set_flipped(self.player_color == 'black')
        self.chess_board.draw()

        # Clear moves
        self.moves_text.config(state='normal')
        self.moves_text.delete('1.0', 'end')
        self.moves_text.config(state='disabled')
        
        # Hide/show buttons based on game mode
        if self.is_practice_mode:
            # Hide online-only buttons in practice mode
            self.resign_btn.pack_forget()
            self.draw_btn.pack_forget()
            # Show back button for practice mode
            self.back_btn.pack(side='left', padx=5, ipady=8)
        else:
            # Show buttons in online mode
            self.resign_btn.pack(side='left', padx=5, ipady=8)
            self.draw_btn.pack(side='left', padx=5, ipady=8)
            # Hide back button in online mode
            self.back_btn.pack_forget()
        
        self.update_turn_label()

    def update_turn_label(self):
        """Update turn label based on current state"""
        # Determine turn from FEN
        fen = self.chess_board.current_fen
        is_white_turn = True
        if fen:
            parts = fen.split()
            if len(parts) > 1 and parts[1] == 'b':
                is_white_turn = False
        
        is_your_turn = (self.player_color == 'white' and is_white_turn) or \
                       (self.player_color == 'black' and not is_white_turn)
        
        if is_your_turn:
            self.turn_label.config(text="Your turn", fg='#27AE60')
        else:
            self.turn_label.config(text="Opponent's turn", fg='#E74C3C')
    
    def on_square_click(self, event):
        """Handle board square click"""
        square = self.chess_board.get_square_from_coords(event.x, event.y)
        if not square:
            return
        
        row, col = square
        piece = self.chess_board.get_piece(row, col)
        print(f"DEBUG: Click at {row},{col}. Piece: '{piece}'")
        
        if self.chess_board.selected_square is None:
            # Select piece - but only if it's the player's piece (or in practice mode)
            if piece and piece != ' ':
                # Check if this is the player's piece
                is_white_piece = piece.isupper()
                is_player_white = self.player_color == 'white'
                
                # In practice mode, allow moving both colors
                can_select = self.is_practice_mode or \
                             (is_white_piece and is_player_white) or \
                             (not is_white_piece and not is_player_white)
                
                if can_select:
                    self.chess_board.selected_square = (row, col)
                    # Get and highlight valid moves
                    valid_moves = self.chess_board.get_valid_moves(row, col)
                    self.chess_board.highlighted_squares = valid_moves
                    self.chess_board.draw()
                else:
                    # Trying to select opponent's piece
                    print(f"DEBUG: Rejected selection. Piece: {piece}, Me: {self.player_color}")
                    self.turn_label.config(text="Not your piece!", fg='orange')
                    # Restore label after 1 second
                    self.root.after(1000, self.update_turn_label)
        else:
            # Check if clicking the same square to deselect
            if self.chess_board.selected_square == (row, col):
                self.chess_board.clear_selection()
            # Check if this is a valid move
            elif (row, col) in self.chess_board.highlighted_squares:
                # Make move
                from_row, from_col = self.chess_board.selected_square
                from_pos = self.chess_board.pos_to_notation(from_row, from_col)
                to_pos = self.chess_board.pos_to_notation(row, col)
                
                # CASTLING UI FIX: If we clicked the Rook, check if it's meant to be a castling move
                # and translate to the standard UCI format (e1g1, e1c1, etc.)
                piece_at_dest = self.chess_board.get_piece(row, col)
                piece_at_source = self.chess_board.get_piece(from_row, from_col)
                
                # Check for Castling via Rook click
                if piece_at_source.lower() == 'k' and piece_at_dest.lower() == 'r':
                    # White Kingside (e1 -> h1 clicked, translates to e1g1)
                    if from_pos == 'e1' and to_pos == 'h1': 
                        to_pos = 'g1'
                    # White Queenside (e1 -> a1 clicked, translates to e1c1)
                    elif from_pos == 'e1' and to_pos == 'a1': 
                        to_pos = 'c1'
                    # Black Kingside (e8 -> h8 clicked, translates to e8g8)
                    elif from_pos == 'e8' and to_pos == 'h8': 
                        to_pos = 'g8'
                    # Black Queenside (e8 -> a8 clicked, translates to e8c8)
                    elif from_pos == 'e8' and to_pos == 'a8': 
                        to_pos = 'c8'

                # Check for Pawn Promotion
                piece = self.chess_board.get_piece(from_row, from_col)
                promotion = ""
                
                if piece:
                     is_white = piece.isupper()
                     is_pawn = piece.lower() == 'p'
                     
                     # Check if reaching last rank
                     # White (P) moves to row 0. Black (p) moves to row 7.
                     # WARNING: 'row' here is destination row.
                     if is_pawn:
                         # Use raw row for logic consistent with promotion
                         if (is_white and row == 0) or (not is_white and row == 7):
                             choice = simpledialog.askstring(
                                 "Promotion", 
                                 "Promote to (q=Queen, r=Rook, b=Bishop, n=Knight):", 
                                 parent=self.root
                             )
                             if choice and choice.lower() in ['q', 'r', 'b', 'n']:
                                 promotion = choice.lower()
                             else:
                                 promotion = 'q' # Default to Queen
                
                if promotion:
                    to_pos += promotion

                # In practice mode, just update local board
                if self.is_practice_mode:
                    # Make move locally
                    self.chess_board.make_move(from_row, from_col, row, col)
                    self.chess_board.clear_selection()
                    self.chess_board.draw()
                    
                    # Add to move history
                    self.add_move(from_pos, to_pos)
                    
                    # Update turn label
                    self.update_turn_label()
                    
                    print(f"DEBUG: Practice mode move: {from_pos} -> {to_pos}")
                # Normal online mode
                elif self.client.connected and self.game_id:
                    # Check connection before sending move
                    if not self.check_connection():
                        messagebox.showerror("Connection Lost", "Cannot send move - disconnected from server")
                        return
                    
                    self.client.make_move(self.game_id, from_pos, to_pos)
                
                    # Clear selection immediately to prevent double submissions
                    self.chess_board.clear_selection()
                    self.chess_board.draw()
                else:
                    print("DEBUG: Cannot make move - not connected or no game_id")
                    self.chess_board.clear_selection()
                    self.chess_board.draw()
            else:
                # Clicking on another piece of the same color - select it instead
                if piece and piece != ' ':
                    is_white_piece = piece.isupper()
                    is_player_white = self.player_color == 'white'
                    
                    # In practice mode, allow selecting any piece
                    can_select = self.is_practice_mode or \
                                 (is_white_piece and is_player_white) or \
                                 (not is_white_piece and not is_player_white)
                    
                    if can_select:
                        self.chess_board.selected_square = (row, col)
                        valid_moves = self.chess_board.get_valid_moves(row, col)
                        self.chess_board.highlighted_squares = valid_moves
                    else:
                        # Clicked on opponent's piece that's not a valid capture
                        self.chess_board.clear_selection()
                else:
                    # Clicked empty square that's not a valid move
                    self.chess_board.clear_selection()
        
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
    
    def return_to_lobby(self):
        """Return to lobby from practice mode"""
        result = messagebox.askyesno("Exit Practice Mode", 
                                     "Do you want to exit practice mode and return to lobby?")
        if result:
            self.hide()
            self.on_game_end(self.player_elo)
    
    def open_chat(self):
        """Open chat (placeholder)"""
        messagebox.showinfo("Chat", "Chat feature coming soon!")
    
    
    def on_move_response(self, msg):
        """Handle move response"""
        payload = msg.get('payload', {})
        # Check success in payload (logic_wrapper now sends success: True)
        # OR check status if success field not present
        is_success = msg.get(PayloadFields.SUCCESS) or payload.get(PayloadFields.SUCCESS) or payload.get(PayloadFields.STATUS) == 'success'
        
        if not is_success:
            error = msg.get(PayloadFields.MESSAGE) or payload.get(PayloadFields.MESSAGE) or 'Invalid move'
            messagebox.showerror("Invalid Move", error)
            # Revert board - Clear selection
            self.chess_board.clear_selection()
            self.chess_board.draw()
        else:
            # Check for Timeout Win FIRST (before FEN check)
            # game_result can be at root level OR in payload
            game_result = msg.get('game_result') or payload.get('game_result')
            if game_result == 'timeout':
                winner_id = msg.get('winner_id') or payload.get('winner_id')
                new_elo = msg.get('new_elo') or payload.get('new_elo')
                
                print(f"DEBUG: Timeout detected! winner_id={winner_id}")
                
                # I claimed, so I won
                fake_end_msg = {
                    'payload': {
                        'result': 'win',
                        'reason': 'timeout',
                        'new_elo': new_elo
                    }
                }
                self.on_game_end_msg(fake_end_msg)
                return
            
            # Valid move confirmed by server
            # Update board state
            next_fen = payload.get(PayloadFields.NEXT_FEN) or msg.get(PayloadFields.NEXT_FEN)
            if next_fen:
                self.chess_board.set_fen(next_fen)
                self.chess_board.draw()
                
                # Update Times
                # MOVE_ACK has times in root msg, MOVE_UPDATE in payload
                time_data = msg if PayloadFields.WHITE_TIME in msg else payload
                self.update_times(time_data)
                
                # Add to history
                from_pos = payload.get(PayloadFields.FROM) or msg.get(PayloadFields.FROM)
                to_pos = payload.get(PayloadFields.TO) or msg.get(PayloadFields.TO)
                if from_pos and to_pos:
                     self.add_move(from_pos, to_pos)
            else:
                 # Fallback if no FEN
                 pass
    
    def on_game_update(self, msg):
        """Handle game update"""
        payload = msg.get('payload', {})
        move = payload.get(PayloadFields.LAST_MOVE) or msg.get(PayloadFields.LAST_MOVE) 
        
        if move:
            # Opponent's move
            from_pos = move.get(PayloadFields.FROM, '?')
            to_pos = move.get(PayloadFields.TO, '?')
            
            # Update board from server state
            fen = payload.get(PayloadFields.FEN)
            if fen:
                self.chess_board.set_fen(fen)
                self.chess_board.draw()
            
            # Update Times
            self.update_times(payload)
            
            # Check for Timeout Loss (Opponent claimed)
            if from_pos == "CLAIM" and to_pos == "TIMEOUT":
                 self.on_game_end_msg({
                     'payload': {
                         'result': 'loss',
                         'reason': 'timeout',
                         # ELO might be missing in MOVE_UPDATE, wait for GAME_END or just show loss
                         'new_elo': None
                     }
                 })
                 return
            
            self.add_move(from_pos, to_pos)

    def update_times(self, payload):
        """Update timer labels from payload"""
        white_time = payload.get(PayloadFields.WHITE_TIME)
        black_time = payload.get(PayloadFields.BLACK_TIME)
        
        if white_time is not None and black_time is not None:
            # Format time mm:ss
            def format_time(seconds):
                m = int(seconds // 60)
                s = int(seconds % 60)
                return f"{m:02d}:{s:02d}"
            
            w_str = format_time(float(white_time))
            b_str = format_time(float(black_time))
            
            # Identify who is who
            if self.player_color == 'white':
                self.player_time_label.config(text=w_str)
                self.opponent_time_label.config(text=b_str)
            else:
                self.player_time_label.config(text=b_str)
                self.opponent_time_label.config(text=w_str)
                
            # Update internal state
            self.white_time_left = float(white_time)
            self.black_time_left = float(black_time)
            # Reset local timer reference
            import time
            self.last_move_time = time.time()
            
            # Reset delay offset after first server update
            self.timer_delay_offset = 0
            
    def check_timeout(self):
        """Check if anyone has timed out"""
        if not self.is_game_active:
            return
        
        # Check connection first
        if not self.check_connection():
            return  # Connection lost, stop checking
            
        if self.last_move_time is None:
             # Timer hasn't started yet (waiting for first move)
             # Or we can just start it now if we want strict start?
             # logic_wrapper says: if last_move_ts_str is None, it's first move, no deduct.
             # So we wait for first move update.
             self.root.after(1000, self.check_timeout)
             return
        
        import time
        now = time.time()
        # Apply delay offset if active
        elapsed = now - self.last_move_time - self.timer_delay_offset
        if elapsed < 0:
            elapsed = 0
        
        # Determine current turn
        fen = self.chess_board.current_fen
        is_white_turn = True
        if fen:
            parts = fen.split()
            if len(parts) > 1 and parts[1] == 'b':
                is_white_turn = False
        
        # Calculate projected time left
        if is_white_turn:
            current_white = self.white_time_left - elapsed
            current_black = self.black_time_left
            
            if current_white <= 0:
                current_white = 0
                # White timed out. 
                # If I am BLACK, I should claim.
                if self.player_color == 'black':
                    if now - self.last_claim_time > 3.0:
                        print("DEBUG: reclaiming timeout on White")
                        self.client.make_move(self.game_id, "CLAIM", "TIMEOUT")
                        self.last_claim_time = now
        else:
            current_white = self.white_time_left
            current_black = self.black_time_left - elapsed
            
            if current_black <= 0:
                current_black = 0
                # Black timed out.
                # If I am WHITE, I should claim.
                if self.player_color == 'white':
                    if now - self.last_claim_time > 3.0:
                        print("DEBUG: reclaiming timeout on Black")
                        self.client.make_move(self.game_id, "CLAIM", "TIMEOUT")
                        self.last_claim_time = now
        
        # Update UI Labels (optional, user said no countdown tick, but showing 00:00 is nice)
        # Actually user said "forget countdown tick", maybe just keep static or update every 1s?
        # Let's simple update labels to show passage of time roughly
        def format_time(seconds):
             m = int(max(0, seconds) // 60)
             s = int(max(0, seconds) % 60)
             return f"{m:02d}:{s:02d}"
             
        if is_white_turn:
             w_str = format_time(current_white)
             # Only update the active one to avoid jitter
             if self.player_color == 'white':
                 self.player_time_label.config(text=w_str)
             else:
                 self.opponent_time_label.config(text=w_str)
        else:
             b_str = format_time(current_black)
             if self.player_color == 'black':
                 self.player_time_label.config(text=b_str)
             else:
                 self.opponent_time_label.config(text=b_str)

        # Re-schedule
        self.root.after(1000, self.check_timeout)
    
    def on_emoji_update(self, msg):
        """Handle emoji/chat update from opponent"""
        emoji = msg.get(PayloadFields.EMOJI, '')
        sender = msg.get(PayloadFields.SENDER, 'Opponent')
        if emoji:
            # Display emoji in chat or as notification
            messagebox.showinfo("Emoji", f"{sender}: {emoji}")
    
    def on_game_end_msg(self, msg):
        """Handle game end"""
        payload = msg.get('payload', {})
        result = payload.get(PayloadFields.RESULT, 'unknown')  # "win", "loss", "draw"
        reason = payload.get(PayloadFields.REASON, 'Game ended')
        new_elo = payload.get(PayloadFields.NEW_ELO, self.player_elo)
        
        self.is_game_active = False # Stop timer checker
        
        # Calculate ELO change
        elo_change = new_elo - self.player_elo if self.player_elo else 0
        
        if result == "win":
            result_text = f"🎉 You Won! 🎉\n\n{reason}\n\nELO: {self.player_elo} → {new_elo} (+{elo_change})"
        elif result == "draw":
            result_text = f"🤝 Draw\n\n{reason}\n\nELO: {self.player_elo} → {new_elo} ({elo_change:+d})"
        else:  # loss
            result_text = f"😞 You Lost\n\n{reason}\n\nELO: {self.player_elo} → {new_elo} ({elo_change})"
        
        # Show custom dialog for rematch request
        self.show_rematch_dialog(result_text, new_elo)
    
    def show_rematch_dialog(self, result_text, new_elo):
        """Show custom dialog for rematch request"""
        # Close any existing dialog
        if self.active_rematch_dialog:
            try:
                self.active_rematch_dialog.destroy()
            except:
                pass
        
        # Create custom dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Game Over")
        dialog.geometry("450x300")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Store reference
        self.active_rematch_dialog = dialog
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Content frame
        content = tk.Frame(dialog, bg='white', padx=30, pady=20)
        content.pack(fill=tk.BOTH, expand=True)
        
        # Result text
        result_label = tk.Label(
            content,
            text=result_text,
            font=("Arial", 12),
            bg='white',
            justify=tk.CENTER
        )
        result_label.pack(pady=20)
        
        # Question
        question_label = tk.Label(
            content,
            text="Do you want to request a rematch?",
            font=("Arial", 11, "bold"),
            bg='white'
        )
        question_label.pack(pady=10)
        
        # Buttons frame
        btn_frame = tk.Frame(content, bg='white')
        btn_frame.pack(pady=20)
        
        def on_yes():
            dialog.destroy()
            self.active_rematch_dialog = None
            # Request rematch
            self.client.request_rematch(self.game_id)
            messagebox.showinfo("Rematch", "Rematch request sent!\nWaiting for opponent's response...")
        
        def on_no():
            dialog.destroy()
            self.active_rematch_dialog = None
            # Return to lobby
            self.hide()
            self.on_game_end(new_elo)
        
        # Yes button
        yes_btn = tk.Button(
            btn_frame,
            text="✓ Yes, Rematch!",
            command=on_yes,
            bg='#27AE60',
            fg='white',
            font=("Arial", 11, "bold"),
            padx=20,
            pady=10,
            relief=tk.FLAT,
            cursor='hand2'
        )
        yes_btn.pack(side=tk.LEFT, padx=10)
        
        # No button
        no_btn = tk.Button(
            btn_frame,
            text="✗ No, Return to Lobby",
            command=on_no,
            bg='#E74C3C',
            fg='white',
            font=("Arial", 11, "bold"),
            padx=20,
            pady=10,
            relief=tk.FLAT,
            cursor='hand2'
        )
        no_btn.pack(side=tk.LEFT, padx=10)
        
        # Handle dialog close button (X)
        dialog.protocol("WM_DELETE_WINDOW", on_no)
    
    def on_rematch_request_received(self, msg):
        """Handle rematch request from opponent"""
        payload = msg.get('payload', {})
        requester_id = payload.get(PayloadFields.REQUESTER_ID)
        game_id = payload.get(PayloadFields.GAME_ID)
        
        # IMPORTANT: Close any existing "request rematch" dialog
        # This ensures opponent's request is shown on top
        if self.active_rematch_dialog:
            try:
                self.active_rematch_dialog.destroy()
                self.active_rematch_dialog = None
                print("DEBUG: Closed active rematch dialog to show opponent's request")
            except:
                pass
        
        # Show opponent's rematch request dialog
        self.show_accept_rematch_dialog(game_id)
    
    def show_accept_rematch_dialog(self, game_id):
        """Show custom dialog to accept/decline opponent's rematch request"""
        # Create custom dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Rematch Request")
        dialog.geometry("400x250")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Bring to front
        dialog.lift()
        dialog.focus_force()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Content frame
        content = tk.Frame(dialog, bg='white', padx=30, pady=20)
        content.pack(fill=tk.BOTH, expand=True)
        
        # Icon
        icon_label = tk.Label(
            content,
            text="⚔️",
            font=("Arial", 48),
            bg='white'
        )
        icon_label.pack(pady=10)
        
        # Message
        msg_label = tk.Label(
            content,
            text="Your opponent wants a rematch!\n\nDo you accept?",
            font=("Arial", 12, "bold"),
            bg='white',
            justify=tk.CENTER
        )
        msg_label.pack(pady=15)
        
        # Buttons frame
        btn_frame = tk.Frame(content, bg='white')
        btn_frame.pack(pady=15)
        
        def on_accept():
            dialog.destroy()
            # Accept rematch
            self.client.accept_rematch(game_id)
            messagebox.showinfo("Rematch", "Rematch accepted!\nStarting new game...")
        
        def on_decline():
            dialog.destroy()
            # Decline rematch
            self.client.decline_rematch(game_id)
            messagebox.showinfo("Rematch", "Rematch declined.")
        
        # Accept button
        accept_btn = tk.Button(
            btn_frame,
            text="✓ Accept",
            command=on_accept,
            bg='#27AE60',
            fg='white',
            font=("Arial", 12, "bold"),
            padx=30,
            pady=10,
            relief=tk.FLAT,
            cursor='hand2'
        )
        accept_btn.pack(side=tk.LEFT, padx=10)
        
        # Decline button
        decline_btn = tk.Button(
            btn_frame,
            text="✗ Decline",
            command=on_decline,
            bg='#E74C3C',
            fg='white',
            font=("Arial", 12, "bold"),
            padx=30,
            pady=10,
            relief=tk.FLAT,
            cursor='hand2'
        )
        decline_btn.pack(side=tk.LEFT, padx=10)
        
        # Handle dialog close button (X) - treat as decline
        dialog.protocol("WM_DELETE_WINDOW", on_decline)
    
    def on_rematch_declined(self, msg):
        """Handle when opponent declines rematch"""
        payload = msg.get('payload', {})
        game_id = payload.get(PayloadFields.GAME_ID)
        
        messagebox.showinfo("Rematch Declined", "Your opponent declined the rematch request.")
        
        # Return to lobby
        self.hide()
        self.on_game_end(self.player_elo)
    
    def on_match_start(self, msg):
        """Handle MATCH_START message - ONLY for rematch"""
        payload = msg.get('payload', {})
        game_id = payload.get(PayloadFields.GAME_ID)
        is_rematch = payload.get('is_rematch', False)
        
        # IMPORTANT: Only handle if this is a rematch
        # Regular MATCH_START from challenge is handled by Lobby screen
        if not is_rematch:
            print(f"DEBUG: MATCH_START received but not rematch - ignoring (Lobby will handle)")
            return
        
        white_id = payload.get('white_id')
        black_id = payload.get('black_id')
        mode = payload.get('mode', 'RAPID')
        time_control = payload.get('time_control')
        
        # Fallback if time_control missing in payload
        if not time_control:
             if mode == 'BLITZ': time_control = "5+0"
             elif mode == 'CLASSICAL': time_control = "30+0"
             else: time_control = "10+0"
        
        print(f"DEBUG: REMATCH MATCH_START - Game {game_id}, white={white_id}, black={black_id}, TC={time_control}")
        
        # For rematch, swap colors from previous game
        if hasattr(self, 'player_color') and self.player_color:
            new_color = 'black' if self.player_color == 'white' else 'white'
            print(f"DEBUG: Rematch - swapping color from {self.player_color} to {new_color}")
        else:
            # Fallback (shouldn't happen in rematch)
            new_color = 'white'
            print(f"WARNING: Rematch but no previous color - defaulting to white")
        
        # Reset and start new game - pass is_rematch=True to avoid re-registering callback
        self.start_game(
            game_id=game_id,
            opponent=self.opponent_name if hasattr(self, 'opponent_name') else "Opponent",
            your_color=new_color,
            opponent_elo=self.opponent_elo if hasattr(self, 'opponent_elo') else 1200,
            player_elo=self.player_elo if hasattr(self, 'player_elo') else 1200,
            time_control=time_control,
            is_rematch=True
        )
    
    def on_draw_offer_received(self, msg):
        """Handle draw offer from opponent"""
        payload = msg.get('payload', {})
        from_id = payload.get('from_id')
        game_id = payload.get('game_id')
        
        # Show confirmation dialog
        response = messagebox.askyesno(
            "Draw Offer",
            f"Your opponent offers a draw.\n\nDo you accept?"
        )
        
        if response:
            # Accept draw - send to network client
            # The C++ client will handle sending DRAW_ACCEPT message
            self.client.accept_draw(game_id)
        else:
            # Decline draw
            self.client.decline_draw(game_id)
    
    def show(self):
        """Show game screen"""
        # Reload theme mỗi khi show screen (user có thể đã thay đổi settings)
        if hasattr(self, 'chess_board') and self.chess_board:
            self.chess_board.load_theme()
            self.chess_board.draw()
        
        self.frame.pack(fill='both', expand=True)
    
    def hide(self):
        """Hide game screen"""
        # Close any active rematch dialog
        if self.active_rematch_dialog:
            try:
                self.active_rematch_dialog.destroy()
                self.active_rematch_dialog = None
            except:
                pass
        
        self.frame.pack_forget()
        
        # Restore Lobby's MATCH_START callback
        if self.lobby_match_start_callback is not None:
            self.client.set_callback(MessageType.MATCH_START, self.lobby_match_start_callback)
            print("DEBUG: Restored Lobby's MATCH_START callback")


# ============== TEST MODE ==============


# ============== TEST MODE ==============
if __name__ == "__main__":
    class MockClient:
        """Mock client for testing without server"""
        def __init__(self):
            self.connected = True
            self.username = "TestPlayer"
            self.callbacks = {}
        
        def set_callback(self, msg_type, callback):
            self.callbacks[msg_type] = callback
        
        def make_move(self, game_id, from_pos, to_pos):
            print(f"[MOCK] Move: {from_pos} -> {to_pos} (game: {game_id})")
            # Simulate server response
            if MessageType.MOVE_ACK in self.callbacks:
                self.callbacks[MessageType.MOVE_ACK]({'success': True})
        
        def resign(self, game_id):
            print(f"[MOCK] Resign from game {game_id}")
        
        def offer_draw(self, game_id):
            print(f"[MOCK] Offer draw in game {game_id}")
    
    # Create test window
    root = tk.Tk()
    root.title("Game Screen Test")
    root.geometry("1200x800")
    root.configure(bg='#ECF0F1')
    
    # Mock client
    mock_client = MockClient()
    
    def on_game_end(new_elo):
        print(f"[MOCK] Game ended, new ELO: {new_elo}")
        root.quit()
    
    # Create game screen
    game_screen = GameScreen(root, mock_client, on_game_end)
    
    # Start a mock game
    game_screen.start_game(
        game_id=12345,
        opponent="OpponentBot",
        your_color="white",
        opponent_elo=1350,
        player_elo=1200
    )
    
    game_screen.show()
    
    print("=" * 50)
    print("Game Screen Test Mode")
    print("=" * 50)
    print("- Click on pieces to select")
    print("- Click on destination to move")
    print("- Test buttons: Resign, Draw, Chat")
    print("=" * 50)
    
    root.mainloop()
