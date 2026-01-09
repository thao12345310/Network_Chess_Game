#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Game Replay Screen - Xem lại các nước đi của ván chơi
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import json
import sys
from pathlib import Path
import chess


class GameReplayScreen:
    """Màn hình replay game với các nút điều khiển"""
    
    def __init__(self, root, on_back):
        self.root = root
        self.on_back = on_back
        
        self.frame = None
        self.game_data = None
        self.moves = []
        self.current_move_index = -1  # -1 = starting position
        self.board = None
        self.is_playing = False
        self.play_speed = 1000  # milliseconds between moves
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI"""
        self.frame = tk.Frame(self.root, bg='#2C3E50')
        
        # Header
        header = tk.Frame(self.frame, bg='#34495E', height=80)
        header.pack(fill=tk.X, padx=20, pady=(20, 10))
        header.pack_propagate(False)
        
        self.title_label = tk.Label(
            header,
            text="🎬 Game Replay",
            font=('Arial', 24, 'bold'),
            bg='#34495E',
            fg='#ECF0F1'
        )
        self.title_label.pack(side=tk.LEFT, padx=20, pady=20)
        
        # Back button
        back_btn = tk.Button(
            header,
            text="← Back",
            font=('Arial', 12),
            bg='#95A5A6',
            fg='white',
            activebackground='#7F8C8D',
            activeforeground='white',
            relief=tk.FLAT,
            cursor='hand2',
            padx=20,
            pady=10,
            command=self.do_back
        )
        back_btn.pack(side=tk.RIGHT, padx=20, pady=20)
        
        # Main content
        content = tk.Frame(self.frame, bg='#2C3E50')
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Left panel - Board
        left_panel = tk.Frame(content, bg='#34495E')
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Board canvas
        self.board_canvas = tk.Canvas(
            left_panel,
            width=600,
            height=600,
            bg='#34495E',
            highlightthickness=0
        )
        self.board_canvas.pack(padx=20, pady=20)
        
        # Right panel - Info and controls
        right_panel = tk.Frame(content, bg='#2C3E50', width=300)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y)
        right_panel.pack_propagate(False)
        
        # Game info
        info_frame = tk.Frame(right_panel, bg='#34495E')
        info_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(
            info_frame,
            text="Game Information",
            font=('Arial', 16, 'bold'),
            bg='#34495E',
            fg='#ECF0F1'
        ).pack(pady=10)
        
        self.info_text = tk.Text(
            info_frame,
            font=('Courier New', 10),
            bg='#2C3E50',
            fg='#ECF0F1',
            height=10,
            width=30,
            relief=tk.FLAT,
            wrap=tk.WORD
        )
        self.info_text.pack(padx=10, pady=10)
        self.info_text.config(state=tk.DISABLED)
        
        # Move list
        moves_frame = tk.Frame(right_panel, bg='#34495E')
        moves_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        tk.Label(
            moves_frame,
            text="Moves",
            font=('Arial', 14, 'bold'),
            bg='#34495E',
            fg='#ECF0F1'
        ).pack(pady=10)
        
        # Scrollbar for moves
        scrollbar = tk.Scrollbar(moves_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.moves_listbox = tk.Listbox(
            moves_frame,
            font=('Courier New', 10),
            bg='#2C3E50',
            fg='#ECF0F1',
            selectbackground='#3498DB',
            selectforeground='white',
            relief=tk.FLAT,
            yscrollcommand=scrollbar.set
        )
        self.moves_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.config(command=self.moves_listbox.yview)
        
        # Bind click to jump to move
        self.moves_listbox.bind('<<ListboxSelect>>', self.on_move_select)
        
        # Control buttons
        controls_frame = tk.Frame(right_panel, bg='#2C3E50')
        controls_frame.pack(fill=tk.X)
        
        # First move button
        tk.Button(
            controls_frame,
            text="⏮",
            font=('Arial', 16),
            bg='#34495E',
            fg='white',
            activebackground='#2C3E50',
            relief=tk.FLAT,
            cursor='hand2',
            width=4,
            command=self.first_move
        ).pack(side=tk.LEFT, padx=2)
        
        # Previous move button
        tk.Button(
            controls_frame,
            text="◀",
            font=('Arial', 16),
            bg='#34495E',
            fg='white',
            activebackground='#2C3E50',
            relief=tk.FLAT,
            cursor='hand2',
            width=4,
            command=self.previous_move
        ).pack(side=tk.LEFT, padx=2)
        
        # Play/Pause button
        self.play_btn = tk.Button(
            controls_frame,
            text="▶",
            font=('Arial', 16),
            bg='#27AE60',
            fg='white',
            activebackground='#229954',
            relief=tk.FLAT,
            cursor='hand2',
            width=4,
            command=self.toggle_play
        )
        self.play_btn.pack(side=tk.LEFT, padx=2)
        
        # Next move button
        tk.Button(
            controls_frame,
            text="▶",
            font=('Arial', 16),
            bg='#34495E',
            fg='white',
            activebackground='#2C3E50',
            relief=tk.FLAT,
            cursor='hand2',
            width=4,
            command=self.next_move
        ).pack(side=tk.LEFT, padx=2)
        
        # Last move button
        tk.Button(
            controls_frame,
            text="⏭",
            font=('Arial', 16),
            bg='#34495E',
            fg='white',
            activebackground='#2C3E50',
            relief=tk.FLAT,
            cursor='hand2',
            width=4,
            command=self.last_move
        ).pack(side=tk.LEFT, padx=2)
        
        # Move counter
        self.move_counter_label = tk.Label(
            right_panel,
            text="Move: 0 / 0",
            font=('Arial', 12),
            bg='#2C3E50',
            fg='#ECF0F1'
        )
        self.move_counter_label.pack(pady=10)
    
    def load_game(self, game_id, game_info):
        """Load game data for replay"""
        try:
            # Call Python logic wrapper to get game details
            logic_path = Path(__file__).parent.parent / 'server' / 'src' / 'game_logic' / 'logic_wrapper.py'
            
            request = {
                "action": "get_game_replay",
                "game_id": game_id
            }
            
            result = subprocess.run(
                [sys.executable, str(logic_path)],
                input=json.dumps(request),
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                response = json.loads(result.stdout)
                if response.get('status') == 'success':
                    self.game_data = response.get('game')
                    self.moves = self.game_data.get('moves', [])
                    self.current_move_index = -1
                    
                    # Initialize chess board
                    self.board = chess.Board()
                    
                    # Update UI
                    self.update_game_info()
                    self.update_moves_list()
                    self.draw_board()
                    self.update_move_counter()
                else:
                    messagebox.showerror("Error", f"Failed to load game: {response.get('message')}")
            else:
                messagebox.showerror("Error", f"Failed to load game: {result.stderr}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error loading game: {str(e)}")
            print(f"Error loading game: {e}")
    
    def update_game_info(self):
        """Update game information display"""
        if not self.game_data:
            return
        
        white = self.game_data.get('white_player', {})
        black = self.game_data.get('black_player', {})
        
        info = f"""
Mode: {self.game_data.get('mode', 'N/A')}

White: {white.get('username', 'N/A')}
ELO: {white.get('elo', 'N/A')}

Black: {black.get('username', 'N/A')}
ELO: {black.get('elo', 'N/A')}

Start: {self.game_data.get('start_time', 'N/A')[:16]}
End: {self.game_data.get('end_time', 'N/A')[:16]}

Status: {self.game_data.get('status', 'N/A')}
        """
        
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete('1.0', tk.END)
        self.info_text.insert('1.0', info.strip())
        self.info_text.config(state=tk.DISABLED)
    
    def update_moves_list(self):
        """Update moves list display"""
        self.moves_listbox.delete(0, tk.END)
        
        if not self.moves:
            return
        
        # Display moves in pairs (white, black)
        for i in range(0, len(self.moves), 2):
            move_num = (i // 2) + 1
            white_move = self.moves[i]
            black_move = self.moves[i + 1] if i + 1 < len(self.moves) else ""
            
            line = f"{move_num}. {white_move:<8} {black_move}"
            self.moves_listbox.insert(tk.END, line)
    
    def draw_board(self):
        """Draw chess board"""
        if not self.board:
            return
        
        self.board_canvas.delete('all')
        
        square_size = 75
        colors = ['#F0D9B5', '#B58863']
        
        # Draw squares
        for row in range(8):
            for col in range(8):
                color = colors[(row + col) % 2]
                x1 = col * square_size
                y1 = row * square_size
                x2 = x1 + square_size
                y2 = y1 + square_size
                
                self.board_canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=color,
                    outline=''
                )
        
        # Draw pieces
        piece_symbols = {
            'P': '♙', 'N': '♘', 'B': '♗', 'R': '♖', 'Q': '♕', 'K': '♔',
            'p': '♟', 'n': '♞', 'b': '♝', 'r': '♜', 'q': '♛', 'k': '♚'
        }
        
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                row = 7 - chess.square_rank(square)
                col = chess.square_file(square)
                
                x = col * square_size + square_size // 2
                y = row * square_size + square_size // 2
                
                symbol = piece_symbols.get(piece.symbol(), piece.symbol())
                color = '#FFFFFF' if piece.color == chess.WHITE else '#000000'
                
                self.board_canvas.create_text(
                    x, y,
                    text=symbol,
                    font=('Arial', 48),
                    fill=color
                )
    
    def update_move_counter(self):
        """Update move counter label"""
        current = self.current_move_index + 1
        total = len(self.moves)
        self.move_counter_label.config(text=f"Move: {current} / {total}")
    
    def first_move(self):
        """Go to first move (starting position)"""
        self.is_playing = False
        self.update_play_button()
        
        self.current_move_index = -1
        self.board = chess.Board()
        self.draw_board()
        self.update_move_counter()
    
    def previous_move(self):
        """Go to previous move"""
        self.is_playing = False
        self.update_play_button()
        
        if self.current_move_index > -1:
            self.current_move_index -= 1
            self.rebuild_board_to_current_move()
    
    def next_move(self):
        """Go to next move"""
        if self.current_move_index < len(self.moves) - 1:
            self.current_move_index += 1
            move_uci = self.moves[self.current_move_index]
            
            try:
                move = chess.Move.from_uci(move_uci)
                self.board.push(move)
                self.draw_board()
                self.update_move_counter()
                
                # Highlight in moves list
                move_pair_index = self.current_move_index // 2
                self.moves_listbox.selection_clear(0, tk.END)
                self.moves_listbox.selection_set(move_pair_index)
                self.moves_listbox.see(move_pair_index)
            except Exception as e:
                print(f"Error making move: {e}")
        else:
            self.is_playing = False
            self.update_play_button()
    
    def last_move(self):
        """Go to last move"""
        self.is_playing = False
        self.update_play_button()
        
        while self.current_move_index < len(self.moves) - 1:
            self.current_move_index += 1
            move_uci = self.moves[self.current_move_index]
            try:
                move = chess.Move.from_uci(move_uci)
                self.board.push(move)
            except Exception as e:
                print(f"Error making move: {e}")
                break
        
        self.draw_board()
        self.update_move_counter()
    
    def rebuild_board_to_current_move(self):
        """Rebuild board from start to current move"""
        self.board = chess.Board()
        
        for i in range(self.current_move_index + 1):
            move_uci = self.moves[i]
            try:
                move = chess.Move.from_uci(move_uci)
                self.board.push(move)
            except Exception as e:
                print(f"Error rebuilding board: {e}")
                break
        
        self.draw_board()
        self.update_move_counter()
    
    def toggle_play(self):
        """Toggle auto-play"""
        self.is_playing = not self.is_playing
        self.update_play_button()
        
        if self.is_playing:
            self.auto_play()
    
    def update_play_button(self):
        """Update play button text"""
        if self.is_playing:
            self.play_btn.config(text="⏸")
        else:
            self.play_btn.config(text="▶")
    
    def auto_play(self):
        """Auto-play moves"""
        if not self.is_playing:
            return
        
        if self.current_move_index < len(self.moves) - 1:
            self.next_move()
            self.root.after(self.play_speed, self.auto_play)
        else:
            self.is_playing = False
            self.update_play_button()
    
    def on_move_select(self, event):
        """Handle move selection from listbox"""
        selection = self.moves_listbox.curselection()
        if not selection:
            return
        
        self.is_playing = False
        self.update_play_button()
        
        # Calculate move index from pair index
        pair_index = selection[0]
        target_move_index = pair_index * 2
        
        # Rebuild board to that move
        self.current_move_index = target_move_index - 1
        self.rebuild_board_to_current_move()
        
        # Make one more move to get to the selected position
        if target_move_index < len(self.moves):
            self.next_move()
    
    def do_back(self):
        """Go back"""
        self.is_playing = False
        self.on_back()
    
    def show(self):
        """Show screen"""
        self.frame.pack(fill=tk.BOTH, expand=True)
    
    def hide(self):
        """Hide screen"""
        self.is_playing = False
        if self.frame:
            self.frame.pack_forget()


# ============== TEST MODE ==============
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Game Replay Test")
    root.geometry("1200x700")
    root.configure(bg='#2C3E50')
    
    def on_back():
        print("Back")
    
    screen = GameReplayScreen(root, on_back=on_back)
    screen.show()
    
    # Test with a sample game
    # You would normally call screen.load_game(game_id, game_info)
    
    root.mainloop()
