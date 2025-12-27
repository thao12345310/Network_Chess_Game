#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Leaderboard Screen - Bảng xếp hạng ELO
"""

import tkinter as tk
from tkinter import ttk


class LeaderboardScreen:
    """Màn hình xem bảng xếp hạng ELO"""
    
    def __init__(self, root, client, on_back):
        self.root = root
        self.client = client
        self.on_back = on_back
        
        # Main frame
        self.frame = tk.Frame(root, bg='#ECF0F1')
        
        self.setup_ui()
        self.client.set_callback('LEADERBOARD', self.on_leaderboard_data)
    
    def setup_ui(self):
        """Setup leaderboard UI"""
        # Top bar
        top_bar = tk.Frame(self.frame, bg='#2C3E50', height=60)
        top_bar.pack(fill='x')
        top_bar.pack_propagate(False)
        
        # Back button
        self.back_btn = tk.Button(top_bar, text="← Back", 
                                  command=self.on_back,
                                  bg='#34495E', fg='white', 
                                  font=("Arial", 10, "bold"),
                                  relief='flat', cursor='hand2',
                                  bd=0, padx=15)
        self.back_btn.pack(side='left', padx=10, pady=10)
        
        # Title
        tk.Label(top_bar, text="🏆 ELO Leaderboard", 
                font=("Arial", 20, "bold"), 
                fg='#F39C12', bg='#2C3E50').pack(pady=10)
        
        # Content
        content = tk.Frame(self.frame, bg='#ECF0F1')
        content.pack(fill='both', expand=True, padx=30, pady=20)
        
        # Podium (Top 3)
        podium_frame = tk.Frame(content, bg='white', relief='solid', bd=1)
        podium_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(podium_frame, text="Top 3 Players", 
                font=("Arial", 16, "bold"), 
                fg='#2C3E50', bg='white').pack(pady=15)
        
        self.podium_container = tk.Frame(podium_frame, bg='white')
        self.podium_container.pack(pady=20)
        
        # Podium positions (2nd, 1st, 3rd)
        self.podium_positions = {}
        medals = ['🥈', '🥇', '🥉']
        heights = [120, 150, 100]
        colors = ['#C0C0C0', '#FFD700', '#CD7F32']
        
        for i, (medal, height, color) in enumerate(zip(medals, heights, colors)):
            pos_frame = tk.Frame(self.podium_container, bg='white')
            pos_frame.pack(side='left', padx=20)
            
            # Player info
            info_frame = tk.Frame(pos_frame, bg=color, relief='raised', bd=2)
            info_frame.pack()
            
            tk.Label(info_frame, text=medal, font=("Arial", 32), 
                    bg=color).pack(pady=10)
            
            username_label = tk.Label(info_frame, text="-", 
                                     font=("Arial", 14, "bold"), 
                                     fg='white', bg=color)
            username_label.pack()
            
            elo_label = tk.Label(info_frame, text="ELO: -", 
                                font=("Arial", 11), 
                                fg='white', bg=color)
            elo_label.pack(pady=5)
            
            # Pedestal
            pedestal = tk.Frame(pos_frame, bg=color, height=height, width=120)
            pedestal.pack(fill='x', pady=5)
            pedestal.pack_propagate(False)
            
            rank = [2, 1, 3][i]
            self.podium_positions[rank] = {
                'username': username_label,
                'elo': elo_label
            }
        
        # Full leaderboard table
        table_frame = tk.Frame(content, bg='white', relief='solid', bd=1)
        table_frame.pack(fill='both', expand=True)
        
        tk.Label(table_frame, text="Full Rankings", 
                font=("Arial", 14, "bold"), 
                fg='#2C3E50', bg='white').pack(pady=15)
        
        # Create treeview
        tree_frame = tk.Frame(table_frame, bg='white')
        tree_frame.pack(fill='both', expand=True, padx=15, pady=10)
        
        columns = ('Rank', 'Player', 'ELO', 'Wins', 'Losses', 'Draws', 'Win Rate')
        self.tree = ttk.Treeview(tree_frame, columns=columns, 
                                show='headings', height=15)
        
        # Configure columns
        self.tree.heading('Rank', text='Rank')
        self.tree.heading('Player', text='Player')
        self.tree.heading('ELO', text='ELO')
        self.tree.heading('Wins', text='Wins')
        self.tree.heading('Losses', text='Losses')
        self.tree.heading('Draws', text='Draws')
        self.tree.heading('Win Rate', text='Win %')
        
        self.tree.column('Rank', width=60, anchor='center')
        self.tree.column('Player', width=180)
        self.tree.column('ELO', width=80, anchor='center')
        self.tree.column('Wins', width=70, anchor='center')
        self.tree.column('Losses', width=70, anchor='center')
        self.tree.column('Draws', width=70, anchor='center')
        self.tree.column('Win Rate', width=80, anchor='center')
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', 
                                 command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        self.tree.pack(side='left', fill='both', expand=True)
        
        # Style for current user
        style = ttk.Style()
        style.configure("Treeview", rowheight=30, font=("Arial", 10))
        self.tree.tag_configure('current_user', background='#3498DB', 
                               foreground='white')
        
        # Refresh button
        refresh_btn = tk.Button(table_frame, text="🔄 Refresh", 
                               command=self.refresh,
                               bg='#27AE60', fg='white', 
                               font=("Arial", 11, "bold"),
                               relief='flat', cursor='hand2')
        refresh_btn.pack(pady=15, ipady=5, ipadx=20)
    
    def refresh(self):
        """Request leaderboard data"""
        self.client.get_leaderboard()
    
    def on_leaderboard_data(self, msg):
        """Handle leaderboard data from server"""
        leaderboard = msg.get('leaderboard', [])
        
        # Update podium (top 3)
        for idx in range(min(3, len(leaderboard))):
            player = leaderboard[idx]
            rank = idx + 1
            username = player.get('username', 'Unknown')
            elo = player.get('elo', 1200)
            
            if rank in self.podium_positions:
                self.podium_positions[rank]['username'].config(text=username)
                self.podium_positions[rank]['elo'].config(text=f"ELO: {elo}")
        
        # Clear and populate table
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for idx, player in enumerate(leaderboard, 1):
            username = player.get('username', 'Unknown')
            elo = player.get('elo', 1200)
            wins = player.get('wins', 0)
            losses = player.get('losses', 0)
            draws = player.get('draws', 0)
            total = wins + losses + draws
            win_rate = f"{(wins/total*100):.1f}%" if total > 0 else "N/A"
            
            # Rank display
            if idx == 1:
                rank_display = "🥇"
            elif idx == 2:
                rank_display = "🥈"
            elif idx == 3:
                rank_display = "🥉"
            else:
                rank_display = str(idx)
            
            # Tag for current user
            tag = 'current_user' if username == self.client.username else ''
            
            self.tree.insert('', 'end', 
                           values=(rank_display, username, elo, wins, 
                                  losses, draws, win_rate),
                           tags=(tag,))
    
    def show(self):
        """Show leaderboard screen"""
        self.frame.pack(fill='both', expand=True)
        self.refresh()
    
    def hide(self):
        """Hide leaderboard screen"""
        self.frame.pack_forget()
