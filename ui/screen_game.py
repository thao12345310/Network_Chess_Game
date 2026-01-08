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
        self.client.set_callback('MOVE_ACK', self.on_move_response)
        self.client.set_callback('MOVE_UPDATE', self.on_game_update)
        self.client.set_callback('EMOJI_UPDATE', self.on_emoji_update)
        self.client.set_callback('GAME_END', self.on_game_end_msg)
        self.client.set_callback('DRAW_OFFER_NOTIFY', self.on_draw_offer_received)
        self.client.set_callback('REMATCH_REQUEST_NOTIFY', self.on_rematch_request_received)
        self.client.set_callback('REMATCH_DECLINED_NOTIFY', self.on_rematch_declined)
    
    def start_game(self, game_id, opponent, your_color, opponent_elo, player_elo):
        """Initialize game with data"""
        print(f"DEBUG: start_game called. Game: {game_id}, Me: {self.client.username}, Color: '{your_color}'")
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
        
        # Set initial turn label
        # Standard chess: White always moves first
        is_white_turn = True 
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
            # Select piece - but only if it's the player's piece
            if piece and piece != ' ':
                # Check if this is the player's piece
                is_white_piece = piece.isupper()
                is_player_white = self.player_color == 'white'
                
                if (is_white_piece and is_player_white) or (not is_white_piece and not is_player_white):
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
                
                # Update local board
                # self.chess_board.make_move(from_row, from_col, row, col) # Disabled for "Check then Move"
                
                # Send to server
                # Send to server
                # Send to server
                if self.client.connected and self.game_id:
                    self.client.make_move(self.game_id, from_pos, to_pos)
                
                # Clear selection immediately to prevent double submissions
                self.chess_board.clear_selection()
                self.chess_board.draw()
            else:
                # Clicking on another piece of the same color - select it instead
                if piece and piece != ' ':
                    is_white_piece = piece.isupper()
                    is_player_white = self.player_color == 'white'
                    
                    if (is_white_piece and is_player_white) or (not is_white_piece and not is_player_white):
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
    
    def open_chat(self):
        """Open chat (placeholder)"""
        messagebox.showinfo("Chat", "Chat feature coming soon!")
    
    
    def on_move_response(self, msg):
        """Handle move response"""
        payload = msg.get('payload', {})
        # Check success in payload (logic_wrapper now sends success: True)
        # OR check status if success field not present
        is_success = msg.get('success') or payload.get('success') or payload.get('status') == 'success'
        
        if not is_success:
            error = msg.get('message') or payload.get('message') or 'Invalid move'
            messagebox.showerror("Invalid Move", error)
            # Revert board - Clear selection
            self.chess_board.clear_selection()
            self.chess_board.draw()
        else:
            # Valid move confirmed by server
            # Update board state
            next_fen = payload.get('next_fen') or msg.get('next_fen')
            if next_fen:
                self.chess_board.set_fen(next_fen)
                self.chess_board.draw()
                
                # Add to history
                from_pos = payload.get('from') or msg.get('from')
                to_pos = payload.get('to') or msg.get('to')
                if from_pos and to_pos:
                     self.add_move(from_pos, to_pos)
            else:
                 # Fallback if no FEN: maybe just make the move?
                 # But we don't have from/to easily here unless we stored it.
                 pass
    
    def on_game_update(self, msg):
        """Handle game update"""
        payload = msg.get('payload', {})
        move = payload.get('last_move') or msg.get('last_move') # Protocol: payload.last_move or top level?
        # My NetworkInterface sends `payload: {last_move: {...}, fen: ...}`. 
        # But `on_game_update_callback` in client might unwrap it?
        # Let's handle both.
        
        if move:
            # Opponent's move
            from_pos = move.get('from', '?')
            to_pos = move.get('to', '?')
            # self.add_move(from_pos, to_pos) # Don't add move yet if we update FEN, or add it here?
            # Ideally update board FEN, then log move.
            
            # Update board from server state
            fen = payload.get('fen')
            if fen:
                self.chess_board.set_fen(fen)
                self.chess_board.draw()
            
            self.add_move(from_pos, to_pos)
    
    def on_emoji_update(self, msg):
        """Handle emoji/chat update from opponent"""
        emoji = msg.get('emoji', '')
        sender = msg.get('from', 'Opponent')
        if emoji:
            # Display emoji in chat or as notification
            messagebox.showinfo("Emoji", f"{sender}: {emoji}")
    
    def on_game_end_msg(self, msg):
        """Handle game end"""
        payload = msg.get('payload', {})
        result = payload.get('result', 'unknown')  # "win", "loss", "draw"
        reason = payload.get('reason', 'Game ended')
        new_elo = payload.get('new_elo', self.player_elo)
        
        # Calculate ELO change
        elo_change = new_elo - self.player_elo if self.player_elo else 0
        
        if result == "win":
            result_text = f"🎉 You Won! 🎉\n\n{reason}\n\nELO: {self.player_elo} → {new_elo} (+{elo_change})"
        elif result == "draw":
            result_text = f"🤝 Draw\n\n{reason}\n\nELO: {self.player_elo} → {new_elo} ({elo_change:+d})"
        else:  # loss
            result_text = f"😞 You Lost\n\n{reason}\n\nELO: {self.player_elo} → {new_elo} ({elo_change})"
        
        # Ask for rematch
        result_text += "\n\nDo you want to request a rematch?"
        
        response = messagebox.askyesno("Game Over", result_text)
        
        if response:
            # Request rematch
            self.client.request_rematch(self.game_id)
            messagebox.showinfo("Rematch", "Rematch request sent!\nWaiting for opponent's response...")
        else:
            # Return to lobby
            self.hide()
            self.on_game_end(new_elo)
    
    def on_rematch_request_received(self, msg):
        """Handle rematch request from opponent"""
        payload = msg.get('payload', {})
        requester_id = payload.get('requester_id')
        game_id = payload.get('game_id')
        
        # Show confirmation dialog
        response = messagebox.askyesno(
            "Rematch Request",
            f"Your opponent wants a rematch!\n\nDo you accept?"
        )
        
        if response:
            # Accept rematch
            self.client.accept_rematch(game_id)
            messagebox.showinfo("Rematch", "Rematch accepted!\nStarting new game...")
        else:
            # Decline rematch
            self.client.decline_rematch(game_id)
            messagebox.showinfo("Rematch", "Rematch declined.")
    
    def on_rematch_declined(self, msg):
        """Handle when opponent declines rematch"""
        payload = msg.get('payload', {})
        game_id = payload.get('game_id')
        
        messagebox.showinfo("Rematch Declined", "Your opponent declined the rematch request.")
        
        # Return to lobby
        self.hide()
        self.on_game_end(self.player_elo)
    
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
        self.frame.pack(fill='both', expand=True)
    
    def hide(self):
        """Hide game screen"""
        self.frame.pack_forget()


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
            if 'MOVE_ACK' in self.callbacks:
                self.callbacks['MOVE_ACK']({'success': True})
        
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
