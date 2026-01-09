#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lobby Screen - Danh sách người chơi và challenge
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime


class LobbyScreen:
    """Màn hình lobby - Tìm đối thủ và xử lý challenge"""
    
    def __init__(self, root, client, player_elo, on_game_start, on_view_leaderboard, on_logout=None, on_view_game_history=None):
        self.root = root
        self.client = client
        self.player_elo = player_elo
        self.on_game_start = on_game_start
        self.on_view_leaderboard = on_view_leaderboard
        self.on_logout = on_logout
        self.on_view_game_history = on_view_game_history
        
        self.players_data = []
        
        # Matchmaking state
        self.is_searching = False
        self.search_start_time = None
        self.search_timer_id = None
        self.matching_dialog = None
        self.MATCHMAKING_TIMEOUT = 60  # Timeout in seconds
        
        # Main frame
        self.frame = tk.Frame(root, bg='#ECF0F1')
        
        self.setup_ui()
        self.setup_callbacks()
    
    def setup_ui(self):
        """Setup lobby UI"""
        # Top bar
        top_bar = tk.Frame(self.frame, bg='#2C3E50', height=60)
        top_bar.pack(fill='x')
        top_bar.pack_propagate(False)
        
        # Title
        tk.Label(top_bar, text="♔ Chess Lobby", 
                font=("Arial", 20, "bold"), 
                fg='#ECF0F1', bg='#2C3E50').pack(side='left', padx=20)
        
        # Player info
        info_frame = tk.Frame(top_bar, bg='#2C3E50')
        info_frame.pack(side='right', padx=20)
        self.logout_btn = tk.Button(info_frame, text="Logout", 
                                    command=self.do_logout,
                                    bg='#E74C3C', fg='white', 
                                    font=("Arial", 9, "bold"),
                                    relief='flat', cursor='hand2')
        self.logout_btn.pack(side='left', padx=10)
        
        # Main content
        content = tk.Frame(self.frame, bg='#ECF0F1')
        content.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Left panel - Actions
        left_panel = tk.Frame(content, bg='white', relief='solid', bd=1)
        left_panel.pack(side='left', fill='y', padx=(0, 10))
        
        tk.Label(left_panel, text="Quick Actions", 
                font=("Arial", 14, "bold"), 
                fg='#2C3E50', bg='white').pack(pady=15, padx=20)
        
        # ========== Game Mode Selection ==========
        mode_frame = tk.Frame(left_panel, bg='white')
        mode_frame.pack(pady=10, padx=20, fill='x')
        
        tk.Label(mode_frame, text="⏱️ Game Mode:", 
                font=("Arial", 11, "bold"), 
                fg='#2C3E50', bg='white').pack(anchor='w')
        
        self.game_mode = tk.StringVar(value="RAPID")
        
        modes_info = [
            ("BLITZ", "⚡ Blitz (5 min)"),
            ("RAPID", "🕐 Rapid (10 min)"),
            ("CLASSICAL", "♔ Classical (30 min)")
        ]
        
        for mode_value, mode_text in modes_info:
            rb = tk.Radiobutton(mode_frame, text=mode_text, 
                               variable=self.game_mode, value=mode_value,
                               font=("Arial", 10), 
                               fg='#34495E', bg='white',
                               activebackground='white',
                               selectcolor='#ECF0F1',
                               cursor='hand2')
            rb.pack(anchor='w', pady=2)
        
        ttk.Separator(left_panel, orient='horizontal').pack(fill='x', 
                                                            pady=10, padx=20)
        
        # Random match button
        self.random_btn = tk.Button(left_panel, text="🎲 Random Match", 
                                    command=self.do_random_match,
                                    bg='#3498DB', fg='white', 
                                    font=("Arial", 12, "bold"),
                                    relief='flat', cursor='hand2',
                                    width=20)
        self.random_btn.pack(pady=10, padx=20, ipady=10)
        
        # View leaderboard
        self.leaderboard_btn = tk.Button(left_panel, text="📊 Leaderboard", 
                                         command=self.on_view_leaderboard,
                                         bg='#F39C12', fg='white', 
                                        font=("Arial", 12, "bold"),
                                         relief='flat', cursor='hand2',
                                         width=20)
        self.leaderboard_btn.pack(pady=10, padx=20, ipady=10)
        
        # Game History button
        if self.on_view_game_history:
            self.history_btn = tk.Button(left_panel, text="📜 Game History", 
                                         command=self.on_view_game_history,
                                         bg='#9B59B6', fg='white', 
                                         font=("Arial", 12, "bold"),
                                         relief='flat', cursor='hand2',
                                         width=20)
            self.history_btn.pack(pady=10, padx=20, ipady=10)
        
        # Refresh players
        self.refresh_btn = tk.Button(left_panel, text="🔄 Refresh Players", 
                                     command=self.refresh_players,
                                     bg='#27AE60', fg='white', 
                                     font=("Arial", 12, "bold"),
                                     relief='flat', cursor='hand2',
                                     width=20)
        self.refresh_btn.pack(pady=10, padx=20, ipady=10)
        
        # Center panel - Players list
        center_panel = tk.Frame(content, bg='white', relief='solid', bd=1)
        center_panel.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Header
        header_frame = tk.Frame(center_panel, bg='#34495E', height=50)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="Online Players", 
                font=("Arial", 14, "bold"), 
                fg='white', bg='#34495E').pack(side='left', padx=20, pady=10)
        
        self.player_count_label = tk.Label(header_frame, text="0 players", 
                                           font=("Arial", 10), 
                                           fg='#BDC3C7', bg='#34495E')
        self.player_count_label.pack(side='right', padx=20)
        
        # Search box
        search_frame = tk.Frame(center_panel, bg='white')
        search_frame.pack(fill='x', padx=15, pady=10)
        
        tk.Label(search_frame, text="🔍", font=("Arial", 12), 
                bg='white').pack(side='left', padx=5)
        
        self.search_entry = tk.Entry(search_frame, font=("Arial", 11), 
                                     relief='solid', bd=1)
        self.search_entry.pack(side='left', fill='x', expand=True)
        self.search_entry.bind('<KeyRelease>', self.filter_players)
        
        # Players listbox
        list_container = tk.Frame(center_panel, bg='white')
        list_container.pack(fill='both', expand=True, padx=15, pady=10)
        
        scrollbar = tk.Scrollbar(list_container)
        scrollbar.pack(side='right', fill='y')
        
        self.players_listbox = tk.Listbox(list_container, 
                                          font=("Courier New", 10),
                                          yscrollcommand=scrollbar.set,
                                          relief='flat',
                                          selectmode='single',
                                          bg='#F8F9FA',
                                          selectbackground='#3498DB',
                                          selectforeground='white')
        self.players_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.players_listbox.yview)
        
        # Challenge button
        self.challenge_btn = tk.Button(center_panel, text="⚔️ Challenge Selected Player", 
                                       command=self.send_challenge,
                                       bg='#E74C3C', fg='white', 
                                       font=("Arial", 11, "bold"),
                                       relief='flat', cursor='hand2')
        self.challenge_btn.pack(fill='x', padx=15, pady=15, ipady=8)
        
        # Right panel - Activity log
        right_panel = tk.Frame(content, bg='white', relief='solid', bd=1, width=300)
        right_panel.pack(side='left', fill='both')
        right_panel.pack_propagate(False)
        
        tk.Label(right_panel, text="Activity Log", 
                font=("Arial", 12, "bold"), 
                fg='#2C3E50', bg='white').pack(pady=10)
        
        self.log_text = scrolledtext.ScrolledText(right_panel, 
                                                  width=30, height=30, 
                                                  font=("Arial", 9),
                                                  state='disabled',
                                                  bg='#F8F9FA')
        self.log_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Auto refresh players on show
        self.refresh_players()
    
    
    def setup_callbacks(self):
        """Setup network callbacks"""
        self.client.set_callback('LOBBY_LIST', self.on_player_list)
        self.client.set_callback('MATCH_START', self.on_game_start_msg)
        self.client.set_callback('MATCH_CANCEL_ACK', self.on_match_cancel_ack)
        self.client.set_callback('CHALLENGE_NOTIFY', self.on_challenge_received)
        self.client.set_callback('CHALLENGE_RESP', self.on_challenge_response)
        self.client.set_callback('ERROR', self.on_error_response)
    
    def refresh_players(self):
        """Refresh player list"""
        if self.client.connected:
            print("DEBUG: Requesting player list...")
            result = self.client.get_player_list()
            print(f"DEBUG: get_player_list() returned: {result}")
            self.log("Refreshing players list...")
        else:
            print("DEBUG: Client not connected!")
    
    def filter_players(self, event=None):
        """Filter players by search"""
        search_text = self.search_entry.get().lower()
        self.players_listbox.delete(0, 'end')
        
        for player in self.players_data:
            username = player.get('username', '')
            if search_text in username.lower():
                self.display_player(player)
    
    def display_player(self, player):
        """Display single player in listbox"""
        username = player.get('username', 'Unknown')
        elo = player.get('elo', 1200)
        status = player.get('status', 'online')
        
        if username == self.client.username:
            return
        
        status_icon = "🟢" if status == 'online' else "🔴"
        display_text = f"{username:20s} ELO:{elo:5d} {status_icon}"
        self.players_listbox.insert('end', display_text)
    
    def send_challenge(self):
        """Send challenge to selected player"""
        selection = self.players_listbox.curselection()
        if not selection:
            messagebox.showinfo("Info", "Please select a player")
            return
        
        selected_text = self.players_listbox.get(selection[0])
        opponent = selected_text.split()[0].strip()
        mode = self.game_mode.get()
        
        # Pass mode to challenge request
        self.client.send_challenge(opponent, mode)
        self.log(f"Challenge sent to {opponent} (Mode: {mode})")
        
        mode_names = {"BLITZ": "5 min", "RAPID": "10 min", "CLASSICAL": "30 min"}
        messagebox.showinfo("Challenge Sent", 
                          f"Challenge sent to {opponent}.\n"
                          f"Mode: {mode} ({mode_names.get(mode, '')})\n"
                          f"Waiting for response...")
    
    def do_random_match(self):
        """Find random opponent with cancel and timeout support"""
        if self.is_searching:
            return
        
        mode = self.game_mode.get()
        mode_names = {"BLITZ": "5 min", "RAPID": "10 min", "CLASSICAL": "30 min"}
        
        # Start matchmaking
        self.client.random_match(mode)
        self.log(f"Searching for random opponent (Mode: {mode})...")
        
        # Set searching state
        self.is_searching = True
        self.search_start_time = datetime.now()
        
        # Disable the random match button while searching
        self.random_btn.config(state='disabled')
        
        # Create matching dialog
        self.show_matching_dialog(mode, mode_names.get(mode, ''))
    
    def show_matching_dialog(self, mode, mode_time):
        """Show a dialog while searching for opponent"""
        self.matching_dialog = tk.Toplevel(self.root)
        self.matching_dialog.title("Finding Opponent...")
        self.matching_dialog.geometry("400x250")
        self.matching_dialog.resizable(False, False)
        self.matching_dialog.transient(self.root)
        self.matching_dialog.grab_set()
        
        # Center the dialog
        self.matching_dialog.update_idletasks()
        x = (self.matching_dialog.winfo_screenwidth() - 400) // 2
        y = (self.matching_dialog.winfo_screenheight() - 250) // 2
        self.matching_dialog.geometry(f"400x250+{x}+{y}")
        
        # Prevent closing via X button
        self.matching_dialog.protocol("WM_DELETE_WINDOW", self.cancel_matching)
        
        # Configure dialog background
        self.matching_dialog.configure(bg='#2C3E50')
        
        # Title
        title_label = tk.Label(self.matching_dialog, 
                              text="🔍 Finding Opponent...",
                              font=("Arial", 18, "bold"),
                              fg='#ECF0F1', bg='#2C3E50')
        title_label.pack(pady=20)
        
        # Mode info
        mode_label = tk.Label(self.matching_dialog,
                             text=f"Mode: {mode} ({mode_time})",
                             font=("Arial", 12),
                             fg='#BDC3C7', bg='#2C3E50')
        mode_label.pack()
        
        # Animated waiting indicator
        self.waiting_var = tk.StringVar(value="Searching...")
        self.waiting_label = tk.Label(self.matching_dialog,
                                      textvariable=self.waiting_var,
                                      font=("Arial", 14),
                                      fg='#3498DB', bg='#2C3E50')
        self.waiting_label.pack(pady=15)
        
        # Timer display
        self.timer_var = tk.StringVar(value=f"Time remaining: {self.MATCHMAKING_TIMEOUT}s")
        self.timer_label = tk.Label(self.matching_dialog,
                                   textvariable=self.timer_var,
                                   font=("Arial", 11),
                                   fg='#F39C12', bg='#2C3E50')
        self.timer_label.pack()
        
        # Cancel button
        cancel_btn = tk.Button(self.matching_dialog,
                              text="❌ Cancel Matching",
                              command=self.cancel_matching,
                              bg='#E74C3C', fg='white',
                              font=("Arial", 12, "bold"),
                              relief='flat', cursor='hand2',
                              width=18)
        cancel_btn.pack(pady=25, ipady=8)
        
        # Start the timer and animation
        self.animation_frame = 0
        self.update_matching_dialog()
    
    def update_matching_dialog(self):
        """Update the matching dialog with animation and timer"""
        if not self.is_searching or not self.matching_dialog:
            return
        
        # Check if dialog still exists
        try:
            self.matching_dialog.winfo_exists()
        except tk.TclError:
            self.is_searching = False
            return
        
        # Calculate elapsed time
        elapsed = (datetime.now() - self.search_start_time).total_seconds()
        remaining = max(0, self.MATCHMAKING_TIMEOUT - int(elapsed))
        
        # Update timer
        self.timer_var.set(f"Time remaining: {remaining}s")
        
        # Update animation
        dots = "." * (self.animation_frame % 4)
        self.waiting_var.set(f"Searching{dots.ljust(3)}")
        self.animation_frame += 1
        
        # Check for timeout
        if elapsed >= self.MATCHMAKING_TIMEOUT:
            self.handle_matching_timeout()
            return
        
        # Schedule next update (every 500ms)
        self.search_timer_id = self.root.after(500, self.update_matching_dialog)
    
    def cancel_matching(self):
        """Cancel the matchmaking process"""
        if not self.is_searching:
            return
        
        # Send cancel request to server
        self.client.cancel_match()
        self.log("Matchmaking cancelled by user")
        
        # Clean up
        self.cleanup_matching()
        
    def handle_matching_timeout(self):
        """Handle matchmaking timeout"""
        if not self.is_searching:
            return
        
        # Send cancel request to server
        self.client.cancel_match()
        self.log("Matchmaking timed out after 60 seconds")
        
        # Clean up
        self.cleanup_matching()
        
        # Show timeout message
        messagebox.showwarning("Matchmaking Timeout",
                              "Could not find an opponent within 60 seconds.\n"
                              "Please try again or select a different game mode.")
    
    def cleanup_matching(self):
        """Clean up matchmaking state"""
        self.is_searching = False
        self.search_start_time = None
        
        # Cancel scheduled timer
        if self.search_timer_id:
            self.root.after_cancel(self.search_timer_id)
            self.search_timer_id = None
        
        # Close dialog
        if self.matching_dialog:
            try:
                self.matching_dialog.destroy()
            except tk.TclError:
                pass
            self.matching_dialog = None
        
        # Re-enable the random match button
        self.random_btn.config(state='normal')
    
    def do_logout(self):
        """Logout and return to login screen"""
        # Cancel any ongoing matchmaking
        if self.is_searching:
            self.cancel_matching()
            
        result = messagebox.askyesno("Logout", "Are you sure you want to logout?")
        if result:
            self.client.logout()
            self.hide()
            # Trigger return to login screen via callback
            if self.on_logout:
                self.on_logout()
    
    def on_player_list(self, msg):
        """Handle player list update"""
        print(f"DEBUG: on_player_list received: {msg}")
        payload = msg.get('payload', {})
        players = payload.get('players', [])
        print(f"DEBUG: Players data: {players}")
        
        # Convert to list of dicts if it's just names
        if players and isinstance(players[0], str):
            self.players_data = [{'username': name, 'elo': 1200, 'status': 'online'} 
                                for name in players]
        else:
            self.players_data = players
        
        self.players_listbox.delete(0, 'end')
        for player in self.players_data:
            self.display_player(player)
        
        self.player_count_label.config(text=f"{len(self.players_data)} players")
        self.log(f"Players online: {len(self.players_data)}")
    
    def on_match_cancel_ack(self, msg):
        """Handle match cancel acknowledgement"""
        print(f"DEBUG: MATCH_CANCEL_ACK received: {msg}")
        payload = msg.get('payload', {})
        status = payload.get('status', '')
        message = payload.get('message', '')
        
        if status == 'cancelled':
            self.log("Server confirmed: Matchmaking cancelled")
        else:
            self.log(f"Cancel response: {message}")
    

    def on_game_start_msg(self, msg):
        """Handle game start message"""
        print(f"DEBUG: MATCH_START received: {msg}")
        
        # Clean up any ongoing matching
        if self.is_searching:
            self.cleanup_matching()
        
        payload = msg.get('payload', {})
        game_id = payload.get('game_id')
        opponent_id = payload.get('opponent_id')
        your_color = payload.get('your_color', 'white')
        opponent_elo = payload.get('opponent_elo', 1200)
        time_control = payload.get('time_control', '10+0')
        
        # Look up opponent username from players_data
        opponent = f"Player {opponent_id}"
        for player in self.players_data:
            if player.get('player_id') == opponent_id:
                opponent = player.get('username', opponent)
                opponent_elo = player.get('elo', 1200)
                break
        
        self.log(f"Game starting vs {opponent}!")
        print(f"DEBUG: Starting game - ID: {game_id}, opponent: {opponent}, color: {your_color}, TC: {time_control}")
        self.hide()
        self.on_game_start(game_id, opponent, your_color, opponent_elo, time_control)
    
    def on_challenge_received(self, msg):
        """Handle incoming challenge from another player"""
        payload = msg.get('payload', {})
        challenger_id = payload.get('challenger_id') or payload.get('from_id')
        
        # Find challenger username from players_data
        challenger_name = f"Player {challenger_id}"
        for player in self.players_data:
            if player.get('player_id') == challenger_id:
                challenger_name = player.get('username', challenger_name)
                break
        
        self.log(f"Challenge received from {challenger_name}!")
        
        mode = payload.get('mode', 'RAPID')
        
        # Show accept/decline dialog
        result = messagebox.askyesno(
            "Challenge Received!",
            f"⚔️ {challenger_name} wants to play chess with you!\nMode: {mode}\n\nDo you accept the challenge?",
            icon='question'
        )
        
        if result:
            # Accept challenge
            self.client.accept_challenge(str(challenger_id), mode)
            self.log(f"Accepted challenge from {challenger_name} ({mode})")
        else:
            # Decline - just don't respond (or send decline)
            self.log(f"Declined challenge from {challenger_name}")
    
    def on_challenge_response(self, msg):
        """Handle challenge response (for debugging)"""
        print(f"DEBUG: CHALLENGE_RESP received: {msg}")
        payload = msg.get('payload', {})
        
        # Check if this is actually a MATCH_START in disguise or an error
        if payload.get('status') == 'declined':
            self.log("Your challenge was declined.")
        elif payload.get('game_id'):
            # This might be a game start disguised as CHALLENGE_RESP
            print(f"DEBUG: Found game_id in CHALLENGE_RESP, treating as game start")
            self.on_game_start_msg(msg)
        else:
            self.log(f"Challenge response: {payload}")
    
    def on_error_response(self, msg):
        """Handle error response"""
        print(f"DEBUG: ERROR received: {msg}")
        payload = msg.get('payload', {})
        reason = payload.get('reason', 'Unknown error')
        self.log(f"Error: {reason}")
        messagebox.showerror("Error", reason)
    
    def log(self, message):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.config(state='normal')
        self.log_text.insert('end', f"[{timestamp}] {message}\n")
        self.log_text.see('end')
        self.log_text.config(state='disabled')
    
    def show(self):
        """Show lobby screen"""
        self.frame.pack(fill='both', expand=True)
        self.refresh_players()
    
    def hide(self):
        """Hide lobby screen"""
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
        
        def get_player_list(self):
            print("[MOCK] Requesting player list...")
            # Simulate server response
            if 'LOBBY_LIST' in self.callbacks:
                mock_response = {
                    'payload': {
                        'players': [
                            {'username': 'Alice', 'elo': 1350, 'status': 'online'},
                            {'username': 'Bob', 'elo': 1200, 'status': 'online'},
                            {'username': 'Charlie', 'elo': 1450, 'status': 'online'},
                            {'username': 'Diana', 'elo': 1100, 'status': 'online'},
                        ]
                    }
                }
                self.callbacks['LOBBY_LIST'](mock_response)
        
        def send_challenge(self, opponent):
            print(f"[MOCK] Challenge sent to: {opponent}")
        
        def random_match(self):
            print("[MOCK] Finding random match...")
        
        def logout(self):
            print("[MOCK] Logged out")
    
    # Create test window
    root = tk.Tk()
    root.title("Lobby Screen Test")
    root.geometry("1200x700")
    root.configure(bg='#ECF0F1')
    
    # Mock client
    mock_client = MockClient()
    
    def on_game_start(game_id, opponent, your_color, opponent_elo):
        print(f"[MOCK] Game started: ID={game_id}, vs {opponent}, color={your_color}")
    
    def on_view_leaderboard():
        print("[MOCK] View leaderboard")
        messagebox.showinfo("Leaderboard", "Leaderboard feature - Coming soon!")
    
    # Create lobby screen
    lobby_screen = LobbyScreen(
        root, 
        mock_client, 
        player_elo=1200,
        on_game_start=on_game_start,
        on_view_leaderboard=on_view_leaderboard
    )
    
    lobby_screen.show()
    
    print("=" * 50)
    print("Lobby Screen Test Mode")
    print("=" * 50)
    print("- Select game mode (BLITZ/RAPID/CLASSICAL)")
    print("- Click 'Random Match' to test matchmaking")
    print("- Select a player and click 'Challenge'")
    print("=" * 50)
    
    root.mainloop()
