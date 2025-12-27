#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Splash Screen - Màn hình khởi động
"""

import tkinter as tk
from tkinter import ttk
import time


class SplashScreen:
    """Splash screen hiển thị khi khởi động app"""
    
    def __init__(self, root, callback):
        self.root = root
        self.callback = callback
        
        # Remove window decorations
        self.window = tk.Toplevel(root)
        self.window.overrideredirect(True)
        
        # Center window
        window_width = 500
        window_height = 400
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Background
        self.window.configure(bg='#2C3E50')
        
        # Main frame
        main_frame = tk.Frame(self.window, bg='#2C3E50')
        main_frame.pack(expand=True, fill='both')
        
        # Logo/Title
        title_label = tk.Label(main_frame, text="♔ Network Chess ♚", 
                              font=("Arial", 36, "bold"), 
                              fg='#ECF0F1', bg='#2C3E50')
        title_label.pack(pady=(80, 20))
        
        # Subtitle
        subtitle = tk.Label(main_frame, text="Online Multiplayer Chess Game", 
                           font=("Arial", 14), 
                           fg='#BDC3C7', bg='#2C3E50')
        subtitle.pack(pady=10)
        
        # Chess pieces animation
        pieces_frame = tk.Frame(main_frame, bg='#2C3E50')
        pieces_frame.pack(pady=30)
        
        pieces = ['♔', '♕', '♖', '♗', '♘', '♙']
        for piece in pieces:
            label = tk.Label(pieces_frame, text=piece, 
                           font=("Arial", 32), 
                           fg='#ECF0F1', bg='#2C3E50')
            label.pack(side='left', padx=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate', 
                                       length=300)
        self.progress.pack(pady=30)
        
        # Status label
        self.status_label = tk.Label(main_frame, text="Loading...", 
                                    font=("Arial", 10), 
                                    fg='#95A5A6', bg='#2C3E50')
        self.status_label.pack(pady=10)
        
        # Version
        version_label = tk.Label(main_frame, text="Version 1.0.0", 
                                font=("Arial", 8), 
                                fg='#7F8C8D', bg='#2C3E50')
        version_label.pack(side='bottom', pady=10)
        
        # Start animation
        self.progress.start(10)
        
        # Auto close after 3 seconds
        self.window.after(3000, self.close)
    
    def update_status(self, text):
        """Update status text"""
        self.status_label.config(text=text)
    
    def close(self):
        """Close splash and call callback"""
        self.progress.stop()
        self.window.destroy()
        self.callback()
