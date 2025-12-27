#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main Application - Screen Manager
"""

import tkinter as tk
from network_client import ChessClient
from screen_splash import SplashScreen
from screen_login import LoginScreen
from screen_lobby import LobbyScreen
from screen_leaderboard import LeaderboardScreen
from screen_game import GameScreen


class ChessApp:
    """Main application with screen management"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Network Chess Game")
        self.root.geometry("1200x800")
        self.root.resizable(False, False)
        
        # Center window
        self.center_window()
        
        # Network client
        self.client = ChessClient()
        
        # Current state
        self.current_screen = None
        self.player_elo = 1200
        
        # Initialize screens
        self.screens = {}
        
        # Show splash screen first
        self.show_splash()
    
    def center_window(self):
        """Center window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def show_splash(self):
        """Show splash screen"""
        SplashScreen(self.root, self.init_screens)
    
    def init_screens(self):
        """Initialize all screens after splash"""
        # Login screen
        self.screens['login'] = LoginScreen(
            self.root, 
            self.client, 
            self.on_login_success
        )
        
        # Lobby screen
        self.screens['lobby'] = LobbyScreen(
            self.root,
            self.client,
            self.player_elo,
            self.on_game_start,
            self.show_leaderboard
        )
        
        # Leaderboard screen
        self.screens['leaderboard'] = LeaderboardScreen(
            self.root,
            self.client,
            self.show_lobby
        )
        
        # Game screen
        self.screens['game'] = GameScreen(
            self.root,
            self.client,
            self.on_game_end
        )
        
        # Show login screen
        self.show_screen('login')
    
    def show_screen(self, screen_name):
        """Switch to a screen"""
        # Hide current screen
        if self.current_screen:
            self.current_screen.hide()
        
        # Show new screen
        if screen_name in self.screens:
            self.current_screen = self.screens[screen_name]
            self.current_screen.show()
    
    def on_login_success(self, elo):
        """Handle successful login"""
        self.player_elo = elo
        self.screens['lobby'].player_elo = elo
        self.show_screen('lobby')
    
    def show_lobby(self):
        """Show lobby screen"""
        self.show_screen('lobby')
    
    def show_leaderboard(self):
        """Show leaderboard screen"""
        self.show_screen('leaderboard')
    
    def on_game_start(self, game_id, opponent, your_color, opponent_elo):
        """Handle game start"""
        self.screens['game'].start_game(
            game_id, 
            opponent, 
            your_color, 
            opponent_elo, 
            self.player_elo
        )
        self.show_screen('game')
    
    def on_game_end(self, new_elo):
        """Handle game end"""
        self.player_elo = new_elo
        self.screens['lobby'].player_elo = new_elo
        self.show_screen('lobby')
    
    def run(self):
        """Run the application"""
        self.root.mainloop()


def main():
    """Main entry point"""
    app = ChessApp()
    app.run()


if __name__ == "__main__":
    main()
