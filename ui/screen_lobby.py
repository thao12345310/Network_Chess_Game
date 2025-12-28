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
    
    def __init__(self, root, client, player_elo, on_game_start, on_view_leaderboard):
        self.root = root
        self.client = client
        self.player_elo = player_elo
        self.on_game_start = on_game_start
        self.on_view_leaderboard = on_view_leaderboard
        
        self.players_data = []
        
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
        
        tk.Label(info_frame, text=f"👤 {self.client.username}", 
                font=("Arial", 12), 
                fg='#ECF0F1', bg='#2C3E50').pack(side='left', padx=10)
        
        tk.Label(info_frame, text=f"⭐ ELO: {self.player_elo}", 
                font=("Arial", 12, "bold"), 
                fg='#F39C12', bg='#2C3E50').pack(side='left', padx=10)
        
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
        
        # Refresh players
        self.refresh_btn = tk.Button(left_panel, text="🔄 Refresh Players", 
                                     command=self.refresh_players,
                                     bg='#27AE60', fg='white', 
                                     font=("Arial", 12, "bold"),
                                     relief='flat', cursor='hand2',
                                     width=20)
        self.refresh_btn.pack(pady=10, padx=20, ipady=10)
        
        ttk.Separator(left_panel, orient='horizontal').pack(fill='x', 
                                                            pady=20, padx=20)
        
        # Stats
        stats_frame = tk.Frame(left_panel, bg='white')
        stats_frame.pack(pady=10, padx=20)
        
        tk.Label(stats_frame, text="Your Stats", 
                font=("Arial", 11, "bold"), 
                fg='#2C3E50', bg='white').pack()
        
        self.stats_text = tk.Text(stats_frame, width=22, height=5, 
                                 font=("Arial", 9),
                                 relief='flat', bg='#ECF0F1')
        self.stats_text.pack(pady=10)
        self.stats_text.insert('end', f"Username: {self.client.username}\n")
        self.stats_text.insert('end', f"ELO: {self.player_elo}\n")
        self.stats_text.insert('end', f"Wins: 0\n")
        self.stats_text.insert('end', f"Losses: 0\n")
        self.stats_text.config(state='disabled')
        
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
        self.client.set_callback('PLAYER_LIST', self.on_player_list)
        self.client.set_callback('CHALLENGE', self.on_challenge)
        self.client.set_callback('CHALLENGE_ACCEPTED', self.on_challenge_accepted)
        self.client.set_callback('CHALLENGE_REJECTED', self.on_challenge_rejected)
        self.client.set_callback('GAME_START', self.on_game_start_msg)
    
    def refresh_players(self):
        """Refresh player list"""
        if self.client.connected:
            self.client.get_player_list()
            self.log("Refreshing players list...")
    
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
        
        self.client.send_challenge(opponent)
        self.log(f"Challenge sent to {opponent}")
        messagebox.showinfo("Challenge Sent", 
                          f"Challenge sent to {opponent}.\nWaiting for response...")
    
    def do_random_match(self):
        """Find random opponent"""
        self.client.random_match()
        self.log("Searching for random opponent...")
        messagebox.showinfo("Searching", "Finding a random opponent...")
    
    def do_logout(self):
        """Logout and return to login screen"""
        result = messagebox.askyesno("Logout", "Are you sure you want to logout?")
        if result:
            self.client.logout()
            self.hide()
            # Should trigger return to login screen
    
    def on_player_list(self, msg):
        """Handle player list update"""
        players = msg.get('players', [])
        self.players_data = players
        
        self.players_listbox.delete(0, 'end')
        for player in players:
            self.display_player(player)
        
        self.player_count_label.config(text=f"{len(players)} players")
        self.log(f"Players online: {len(players)}")
    
    def on_challenge(self, msg):
        """Handle incoming challenge"""
        challenger = msg.get('challenger')
        challenger_elo = msg.get('challenger_elo', 1200)
        
        result = messagebox.askyesno("Challenge Received", 
                                     f"⚔️ {challenger} (ELO: {challenger_elo})\n\n"
                                     f"challenged you to a game!\n\nAccept?",
                                     icon='question')
        if result:
            self.client.accept_challenge(challenger)
            self.log(f"✅ Accepted challenge from {challenger}")
        else:
            self.client.reject_challenge(challenger)
            self.log(f"❌ Rejected challenge from {challenger}")
    
    def on_challenge_accepted(self, msg):
        """Handle challenge accepted"""
        opponent = msg.get('opponent')
        self.log(f"✅ {opponent} accepted your challenge!")
        messagebox.showinfo("Accepted", f"{opponent} accepted!")
    
    def on_challenge_rejected(self, msg):
        """Handle challenge rejected"""
        opponent = msg.get('opponent')
        self.log(f"❌ {opponent} rejected your challenge")
        messagebox.showinfo("Rejected", f"{opponent} declined")
    
    def on_game_start_msg(self, msg):
        """Handle game start message"""
        game_id = msg.get('game_id')
        opponent = msg.get('opponent')
        your_color = msg.get('your_color', 'white')
        opponent_elo = msg.get('opponent_elo', 1200)
        
        self.log(f"Game starting vs {opponent}!")
        self.hide()
        self.on_game_start(game_id, opponent, your_color, opponent_elo)
    
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
