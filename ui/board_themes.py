#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chess Board Themes and Appearance Settings
"""

class BoardTheme:
    """Định nghĩa theme cho bàn cờ"""
    
    # Predefined themes
    THEMES = {
        'classic': {
            'name': 'Classic',
            'light_square': '#F0D9B5',
            'dark_square': '#B58863',
            'selected': '#BACA44',
            'valid_move_light': '#AED581',
            'valid_move_dark': '#8BC34A',
            'capture_ring': '#E53935',
            'move_indicator': '#555555'
        },
        'wood': {
            'name': 'Wood',
            'light_square': '#D4A574',
            'dark_square': '#8B5A3C',
            'selected': '#C4A860',
            'valid_move_light': '#B8956E',
            'valid_move_dark': '#9B7653',
            'capture_ring': '#D32F2F',
            'move_indicator': '#4A4A4A'
        },
        'dark': {
            'name': 'Dark',
            'light_square': '#4A4A4A',
            'dark_square': '#2C2C2C',
            'selected': '#5C5C3C',
            'valid_move_light': '#5A5A5A',
            'valid_move_dark': '#3C3C3C',
            'capture_ring': '#FF5252',
            'move_indicator': '#CCCCCC'
        },
        'modern': {
            'name': 'Modern',
            'light_square': '#EEEEEE',
            'dark_square': '#6C7A89',
            'selected': '#FFC107',
            'valid_move_light': '#B2DFDB',
            'valid_move_dark': '#80CBC4',
            'capture_ring': '#FF5722',
            'move_indicator': '#424242'
        },
        'blue': {
            'name': 'Ocean Blue',
            'light_square': '#B3E5FC',
            'dark_square': '#4FC3F7',
            'selected': '#81C784',
            'valid_move_light': '#A5D6A7',
            'valid_move_dark': '#66BB6A',
            'capture_ring': '#E91E63',
            'move_indicator': '#1565C0'
        },
        'purple': {
            'name': 'Royal Purple',
            'light_square': '#E1BEE7',
            'dark_square': '#9C27B0',
            'selected': '#FFB74D',
            'valid_move_light': '#CE93D8',
            'valid_move_dark': '#AB47BC',
            'capture_ring': '#F44336',
            'move_indicator': '#4A148C'
        },
        'green': {
            'name': 'Forest Green',
            'light_square': '#C5E1A5',
            'dark_square': '#558B2F',
            'selected': '#FDD835',
            'valid_move_light': '#AED581',
            'valid_move_dark': '#7CB342',
            'capture_ring': '#D32F2F',
            'move_indicator': '#1B5E20'
        }
    }
    
    # Piece styles (Unicode symbols)
    PIECE_STYLES = {
        'classic': {
            'name': 'Classic',
            'pieces': {
                'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔', 'P': '♙',
                'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚', 'p': '♟'
            },
            'font': ('Arial', 48),
            'color': 'black'
        },
        'bold': {
            'name': 'Bold',
            'pieces': {
                'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔', 'P': '♙',
                'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚', 'p': '♟'
            },
            'font': ('Arial Black', 52),
            'color': '#1A1A1A'
        },
        'modern': {
            'name': 'Modern',
            'pieces': {
                'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔', 'P': '♙',
                'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚', 'p': '♟'
            },
            'font': ('Segoe UI', 50),
            'color': '#2C3E50'
        },
        'elegant': {
            'name': 'Elegant',
            'pieces': {
                'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔', 'P': '♙',
                'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚', 'p': '♟'
            },
            'font': ('Georgia', 48),
            'color': '#000000'
        }
    }
    
    @staticmethod
    def get_theme(theme_name='classic'):
        """Lấy theme theo tên"""
        return BoardTheme.THEMES.get(theme_name, BoardTheme.THEMES['classic'])
    
    @staticmethod
    def get_piece_style(style_name='classic'):
        """Lấy piece style theo tên"""
        return BoardTheme.PIECE_STYLES.get(style_name, BoardTheme.PIECE_STYLES['classic'])
    
    @staticmethod
    def get_all_theme_names():
        """Lấy danh sách tên tất cả themes"""
        return [(k, v['name']) for k, v in BoardTheme.THEMES.items()]
    
    @staticmethod
    def get_all_piece_style_names():
        """Lấy danh sách tên tất cả piece styles"""
        return [(k, v['name']) for k, v in BoardTheme.PIECE_STYLES.items()]
