#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Game History Screen - Xem lịch sử các ván đã chơi
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import json
import sys
from pathlib import Path


class GameHistoryScreen:
    """Màn hình hiển thị lịch sử các ván đã chơi"""
    
    def __init__(self, root, player_id, on_replay, on_back):
        self.root = root
        self.player_id = player_id
        self.on_replay = on_replay  # Callback để mở replay screen
        self.on_back = on_back  # Callback để quay lại lobby
        
        self.frame = None
        self.games = []
        
        self.setup_ui()
        self.load_game_history()
    
    def setup_ui(self):
        """Setup UI"""
        self.frame = tk.Frame(self.root, bg='#2C3E50')
        
        # Header
        header = tk.Frame(self.frame, bg='#34495E', height=80)
        header.pack(fill=tk.X, padx=20, pady=(20, 10))
        header.pack_propagate(False)
        
        title = tk.Label(
            header,
            text="📜 Game History",
            font=('Arial', 24, 'bold'),
            bg='#34495E',
            fg='#ECF0F1'
        )
        title.pack(side=tk.LEFT, padx=20, pady=20)
        
        # Back button
        back_btn = tk.Button(
            header,
            text="← Back to Lobby",
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
        
        # Main content area
        content = tk.Frame(self.frame, bg='#2C3E50')
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Games list with scrollbar
        list_frame = tk.Frame(content, bg='#34495E')
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Listbox for games
        self.games_listbox = tk.Listbox(
            list_frame,
            font=('Courier New', 11),
            bg='#34495E',
            fg='#ECF0F1',
            selectbackground='#3498DB',
            selectforeground='white',
            relief=tk.FLAT,
            yscrollcommand=scrollbar.set,
            height=20
        )
        self.games_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.games_listbox.yview)
        
        # Bind double-click to view replay
        self.games_listbox.bind('<Double-Button-1>', self.on_game_double_click)
        
        # Button frame
        btn_frame = tk.Frame(content, bg='#2C3E50')
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        # View Replay button
        replay_btn = tk.Button(
            btn_frame,
            text="🎬 View Replay",
            font=('Arial', 14, 'bold'),
            bg='#27AE60',
            fg='white',
            activebackground='#229954',
            activeforeground='white',
            relief=tk.FLAT,
            cursor='hand2',
            padx=30,
            pady=15,
            command=self.view_selected_replay
        )
        replay_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Refresh button
        refresh_btn = tk.Button(
            btn_frame,
            text="🔄 Refresh",
            font=('Arial', 14),
            bg='#3498DB',
            fg='white',
            activebackground='#2E86C1',
            activeforeground='white',
            relief=tk.FLAT,
            cursor='hand2',
            padx=30,
            pady=15,
            command=self.load_game_history
        )
        refresh_btn.pack(side=tk.LEFT)
        
        # Info label
        self.info_label = tk.Label(
            content,
            text="Loading game history...",
            font=('Arial', 10),
            bg='#2C3E50',
            fg='#95A5A6'
        )
        self.info_label.pack(pady=10)
    
    def load_game_history(self):
        """Load game history from server"""
        try:
            # Call Python logic wrapper directly
            logic_path = Path(__file__).parent.parent / 'server' / 'src' / 'game_logic' / 'logic_wrapper.py'
            
            request = {
                "action": "get_game_history",
                "player_id": self.player_id
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
                    self.games = response.get('games', [])
                    self.display_games()
                else:
                    self.info_label.config(text=f"Error: {response.get('message', 'Unknown error')}")
            else:
                self.info_label.config(text=f"Failed to load game history: {result.stderr}")
                
        except Exception as e:
            self.info_label.config(text=f"Error loading game history: {str(e)}")
            print(f"Error loading game history: {e}")
    
    def display_games(self):
        """Display games in listbox"""
        self.games_listbox.delete(0, tk.END)
        
        if not self.games:
            self.info_label.config(text="No games found. Play some games first!")
            return
        
        self.info_label.config(text=f"Found {len(self.games)} game(s)")
        
        # Header
        header = f"{'Date':<20} {'Mode':<12} {'Opponent':<20} {'Color':<8} {'Result':<8}"
        self.games_listbox.insert(tk.END, header)
        self.games_listbox.insert(tk.END, "=" * 80)
        
        for game in self.games:
            # Format date
            end_time = game.get('end_time', '')
            if 'T' in end_time:
                date_str = end_time.split('T')[0]
            else:
                date_str = end_time[:10] if len(end_time) >= 10 else end_time
            
            # Format result with color
            result = game.get('result', 'UNKNOWN')
            
            # Create display line
            line = f"{date_str:<20} {game.get('mode', 'N/A'):<12} {game.get('opponent_username', 'N/A'):<20} {game.get('player_color', 'N/A'):<8} {result:<8}"
            self.games_listbox.insert(tk.END, line)
    
    def on_game_double_click(self, event):
        """Handle double-click on game"""
        self.view_selected_replay()
    
    def view_selected_replay(self):
        """View replay of selected game"""
        selection = self.games_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a game to replay")
            return
        
        # Get selected index (subtract 2 for header lines)
        index = selection[0] - 2
        if index < 0 or index >= len(self.games):
            messagebox.showwarning("Invalid Selection", "Please select a valid game")
            return
        
        game = self.games[index]
        game_id = game.get('game_id')
        
        if game_id:
            self.on_replay(game_id, game)
    
    def do_back(self):
        """Go back to lobby"""
        self.on_back()
    
    def show(self):
        """Show screen"""
        self.frame.pack(fill=tk.BOTH, expand=True)
        self.load_game_history()
    
    def hide(self):
        """Hide screen"""
        if self.frame:
            self.frame.pack_forget()


# ============== TEST MODE ==============
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Game History Test")
    root.geometry("900x700")
    root.configure(bg='#2C3E50')
    
    def on_replay(game_id, game):
        print(f"Replay game {game_id}: {game}")
    
    def on_back():
        print("Back to lobby")
    
    # Test with player_id = 1
    screen = GameHistoryScreen(root, player_id=1, on_replay=on_replay, on_back=on_back)
    screen.show()
    
    root.mainloop()
