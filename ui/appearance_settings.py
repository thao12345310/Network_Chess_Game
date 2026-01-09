#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Board Appearance Settings Manager
Lưu và load preferences của user
"""

import json
import os


class AppearanceSettings:
    """Quản lý settings giao diện bàn cờ"""
    
    SETTINGS_FILE = 'board_settings.json'
    
    DEFAULT_SETTINGS = {
        'board_theme': 'classic',
        'piece_style': 'classic',
        'show_coordinates': True,
        'show_legal_moves': True,
        'square_size': 80
    }
    
    def __init__(self):
        self.settings = self.load_settings()
    
    def load_settings(self):
        """Load settings từ file"""
        try:
            if os.path.exists(self.SETTINGS_FILE):
                with open(self.SETTINGS_FILE, 'r') as f:
                    loaded = json.load(f)
                    # Merge với default để đảm bảo có đủ keys
                    settings = self.DEFAULT_SETTINGS.copy()
                    settings.update(loaded)
                    
                    # Save lại để update file với missing keys
                    if set(loaded.keys()) != set(self.DEFAULT_SETTINGS.keys()):
                        self.settings = settings
                        self.save_settings()
                    
                    return settings
        except Exception as e:
            print(f"Error loading settings: {e}")
        
        # Return defaults nếu không load được
        return self.DEFAULT_SETTINGS.copy()
    
    def save_settings(self):
        """Save settings ra file"""
        try:
            with open(self.SETTINGS_FILE, 'w') as f:
                json.dump(self.settings, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def get(self, key, default=None):
        """Lấy giá trị setting"""
        return self.settings.get(key, default)
    
    def set(self, key, value):
        """Set giá trị setting"""
        self.settings[key] = value
        self.save_settings()
    
    def reset_to_defaults(self):
        """Reset về default settings"""
        self.settings = self.DEFAULT_SETTINGS.copy()
        self.save_settings()
