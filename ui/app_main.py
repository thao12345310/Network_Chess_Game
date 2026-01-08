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
from screen_appearance import AppearanceScreen
from appearance_settings import AppearanceSettings
from screen_game_history import GameHistoryScreen
from screen_game_replay import GameReplayScreen



class ChessApp:
    """Main application with screen management"""
    
    def __init__(self, host='127.0.0.1', port=5001):
        self.root = tk.Tk()
        self.root.title("Network Chess Game")
        self.root.geometry("1200x800")
        self.root.resizable(False, False)
        
        # Center window
        self.center_window()
        
        # Network client
        self.client = ChessClient(host=host, port=port)
        
        # Appearance settings (shared across screens)
        self.appearance_settings = AppearanceSettings()
        
        # Current state
        self.current_screen = None
        self.player_elo = 1200
        self.player_id = None  # Store player ID for game history
        
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
            self.show_leaderboard,
            self.on_logout,
            self.show_game_history,
            self.show_appearance_settings
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
            self.on_game_end,
            self.appearance_settings
        )
        
        # Appearance settings screen
        self.screens['appearance'] = AppearanceScreen(
            self.root,
            self.appearance_settings,
            self.show_lobby
        )
        
        # Game History screen (will be initialized after login)
        self.screens['game_history'] = None
        
        # Game Replay screen
        self.screens['game_replay'] = GameReplayScreen(
            self.root,
            self.show_game_history
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
    
    def on_login_success(self, elo, player_id=None):
        """Handle successful login"""
        self.player_elo = elo
        self.player_id = player_id
        self.screens['lobby'].player_elo = elo
        
        # Initialize game history screen now that we have player_id
        if player_id and not self.screens['game_history']:
            self.screens['game_history'] = GameHistoryScreen(
                self.root,
                player_id,
                self.show_game_replay,
                self.show_lobby
            )
        
        self.show_screen('lobby')
    
    def show_lobby(self):
        """Show lobby screen"""
        self.show_screen('lobby')
    
    def show_leaderboard(self):
        """Show leaderboard screen"""
        self.show_screen('leaderboard')
    
    def show_appearance_settings(self):
        """Show appearance settings screen"""
        self.show_screen('appearance')
    def show_game_history(self):
        """Show game history screen"""
        if self.screens['game_history']:
            self.show_screen('game_history')
        else:
            print("Game history not initialized - player_id missing")
    
    def show_game_replay(self, game_id, game_info):
        """Show game replay screen"""
        self.screens['game_replay'].load_game(game_id, game_info)
        self.show_screen('game_replay')
    
    def on_game_start(self, game_id, opponent, your_color, opponent_elo, time_control="10+0"):
        """Handle game start"""
        self.screens['game'].start_game(
            game_id, 
            opponent, 
            your_color, 
            opponent_elo, 
            self.player_elo,
            time_control
        )
        self.show_screen('game')
    
    def on_game_end(self, new_elo):
        """Handle game end"""
        self.player_elo = new_elo
        self.screens['lobby'].player_elo = new_elo
        self.show_screen('lobby')
    
    def on_logout(self):
        """Handle logout - return to login screen"""
        # Reset client state
        self.player_elo = 1200
        self.player_id = None
        # Show login screen
        self.show_screen('login')
    
    def run(self):
        """Run the application"""
        self.root.mainloop()


def main():
    """Main entry point"""
    app = ChessApp()
    app.run()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Network Chess Client')
    parser.add_argument('--host', default='127.0.0.1', help='Server IP address')
    parser.add_argument('--port', type=int, default=5001, help='Server port')
    args = parser.parse_args()

    app = ChessApp(host=args.host, port=args.port)
    app.run()
