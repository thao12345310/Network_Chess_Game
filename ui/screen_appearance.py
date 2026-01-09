#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Board Appearance Settings Screen
"""

import tkinter as tk
from tkinter import ttk
from board_themes import BoardTheme
from appearance_settings import AppearanceSettings


class AppearanceScreen:
    """Màn hình settings cho board appearance"""
    
    def __init__(self, parent, appearance_settings, on_back):
        self.parent = parent
        self.appearance_settings = appearance_settings
        self.on_back = on_back
        
        self.frame = tk.Frame(parent, bg="#34495E")
        
        # Preview board
        self.preview_board = None
        
        self.create_widgets()
    
    def create_widgets(self):
        """Tạo UI elements"""
        # Title
        title = tk.Label(
            self.frame,
            text="⚙️ Board Appearance Settings",
            font=("Arial", 24, "bold"),
            bg="#34495E",
            fg="white"
        )
        title.pack(pady=10)
        
        # Create canvas with scrollbar for all content
        canvas_container = tk.Frame(self.frame, bg="#34495E")
        canvas_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))
        
        # Scrollbar
        scrollbar = tk.Scrollbar(canvas_container, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Canvas
        self.canvas = tk.Canvas(
            canvas_container,
            bg="#34495E",
            yscrollcommand=scrollbar.set,
            highlightthickness=0
        )
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.canvas.yview)
        
        # Settings container inside canvas - 2 column layout
        settings_frame = tk.Frame(self.canvas, bg="#2C3E50", padx=30, pady=20)
        canvas_window = self.canvas.create_window((0, 0), window=settings_frame, anchor=tk.NW)
        
        # Configure canvas scroll region
        def configure_scroll_region(event):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            # Update canvas window width to match canvas width
            canvas_width = event.width
            self.canvas.itemconfig(canvas_window, width=canvas_width)
        
        self.canvas.bind('<Configure>', configure_scroll_region)
        settings_frame.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        # Mouse wheel scrolling
        def on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        self.canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        # Create 2 columns
        left_column = tk.Frame(settings_frame, bg="#2C3E50")
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        right_column = tk.Frame(settings_frame, bg="#2C3E50")
        right_column.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 0))
        
        # Left column - Settings
        # Board Theme Section
        self.create_theme_section(left_column)
        
        # Piece Style Section
        self.create_piece_style_section(left_column)
        
        # Display Options Section
        self.create_display_options(left_column)
        
        # Right column - Preview
        # Preview Section
        self.create_preview_section(right_column)
        
        # Buttons at bottom of left column
        self.create_buttons(left_column)
    
    def create_theme_section(self, parent):
        """Tạo section chọn board theme"""
        section = tk.LabelFrame(
            parent,
            text="🎨 Board Theme",
            font=("Arial", 14, "bold"),
            bg="#34495E",
            fg="white",
            padx=20,
            pady=15
        )
        section.pack(fill=tk.X, pady=10)
        
        # Theme buttons grid
        themes = BoardTheme.get_all_theme_names()
        current_theme = self.appearance_settings.get('board_theme', 'classic')
        
        self.theme_var = tk.StringVar(value=current_theme)
        
        col = 0
        row = 0
        for theme_id, theme_name in themes:
            btn = tk.Radiobutton(
                section,
                text=theme_name,
                variable=self.theme_var,
                value=theme_id,
                font=("Arial", 12),
                bg="#34495E",
                fg="white",
                selectcolor="#2C3E50",
                activebackground="#3E5771",
                activeforeground="white",
                command=self.on_theme_changed
            )
            btn.grid(row=row, column=col, padx=10, pady=5, sticky=tk.W)
            
            col += 1
            if col >= 3:
                col = 0
                row += 1
    
    def create_piece_style_section(self, parent):
        """Tạo section chọn piece style"""
        section = tk.LabelFrame(
            parent,
            text="♟️ Piece Style",
            font=("Arial", 14, "bold"),
            bg="#34495E",
            fg="white",
            padx=20,
            pady=15
        )
        section.pack(fill=tk.X, pady=10)
        
        styles = BoardTheme.get_all_piece_style_names()
        current_style = self.appearance_settings.get('piece_style', 'classic')
        
        self.piece_style_var = tk.StringVar(value=current_style)
        
        for style_id, style_name in styles:
            btn = tk.Radiobutton(
                section,
                text=style_name,
                variable=self.piece_style_var,
                value=style_id,
                font=("Arial", 12),
                bg="#34495E",
                fg="white",
                selectcolor="#2C3E50",
                activebackground="#3E5771",
                activeforeground="white",
                command=self.on_piece_style_changed
            )
            btn.pack(anchor=tk.W, pady=3)
    
    def create_display_options(self, parent):
        """Tạo section display options"""
        section = tk.LabelFrame(
            parent,
            text="🔧 Display Options",
            font=("Arial", 14, "bold"),
            bg="#34495E",
            fg="white",
            padx=20,
            pady=15
        )
        section.pack(fill=tk.X, pady=10)
        
        # Show coordinates checkbox
        self.show_coords_var = tk.BooleanVar(
            value=self.appearance_settings.get('show_coordinates', True)
        )
        coords_check = tk.Checkbutton(
            section,
            text="Show Coordinates (a-h, 1-8)",
            variable=self.show_coords_var,
            font=("Arial", 12),
            bg="#34495E",
            fg="white",
            selectcolor="#2C3E50",
            activebackground="#3E5771",
            activeforeground="white",
            command=self.on_display_option_changed
        )
        coords_check.pack(anchor=tk.W, pady=5)
        
        # Show legal moves checkbox
        self.show_legal_var = tk.BooleanVar(
            value=self.appearance_settings.get('show_legal_moves', True)
        )
        legal_check = tk.Checkbutton(
            section,
            text="Show Legal Move Indicators",
            variable=self.show_legal_var,
            font=("Arial", 12),
            bg="#34495E",
            fg="white",
            selectcolor="#2C3E50",
            activebackground="#3E5771",
            activeforeground="white",
            command=self.on_display_option_changed
        )
        legal_check.pack(anchor=tk.W, pady=5)
    
    def create_preview_section(self, parent):
        """Tạo preview board"""
        section = tk.LabelFrame(
            parent,
            text="👁️ Preview",
            font=("Arial", 14, "bold"),
            bg="#34495E",
            fg="white",
            padx=20,
            pady=10
        )
        section.pack(fill=tk.X, pady=10)
        
        # Mini board canvas (4x4 for preview) - smaller size
        canvas_size = 280  # 4 squares * 70px
        self.preview_canvas = tk.Canvas(
            section,
            width=canvas_size,
            height=canvas_size,
            bg="#2C3E50",
            highlightthickness=0
        )
        self.preview_canvas.pack(pady=10)
        
        self.draw_preview()
    
    def draw_preview(self):
        """Vẽ preview board 4x4"""
        self.preview_canvas.delete("all")
        
        theme_name = self.theme_var.get()
        style_name = self.piece_style_var.get()
        
        theme = BoardTheme.get_theme(theme_name)
        style = BoardTheme.get_piece_style(style_name)
        
        square_size = 70  # Smaller squares for preview
        
        # Sample pieces for preview (4x4)
        preview_pieces = [
            ['r', 'n', 'b', 'q'],
            ['p', 'p', 'p', 'p'],
            ['P', 'P', 'P', 'P'],
            ['R', 'N', 'B', 'Q']
        ]
        
        show_coords = self.show_coords_var.get()
        
        for row in range(4):
            for col in range(4):
                x1 = col * square_size
                y1 = row * square_size
                x2 = x1 + square_size
                y2 = y1 + square_size
                
                color = theme['light_square'] if (row + col) % 2 == 0 else theme['dark_square']
                
                self.preview_canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="gray")
                
                # Draw piece
                piece = preview_pieces[row][col]
                if piece != ' ':
                    piece_symbol = style['pieces'].get(piece, piece)
                    # Scale down font for preview
                    original_font = style['font']
                    preview_font = (original_font[0], int(original_font[1] * 0.7))
                    piece_color = style['color']
                    
                    self.preview_canvas.create_text(
                        x1 + square_size/2, y1 + square_size/2,
                        text=piece_symbol, font=preview_font, fill=piece_color
                    )
        
        # Draw sample coordinates if enabled
        if show_coords:
            for i in range(4):
                label = chr(97 + i)  # a-d
                self.preview_canvas.create_text(
                    i * square_size + square_size/2, 4 * square_size + 10,
                    text=label, font=("Arial", 10)
                )
                label = str(4 - i)  # 4-1
                self.preview_canvas.create_text(
                    -10, i * square_size + square_size/2,
                    text=label, font=("Arial", 10)
                )
    
    def create_buttons(self, parent):
        """Tạo buttons"""
        btn_frame = tk.Frame(parent, bg="#2C3E50")
        btn_frame.pack(pady=15)
        
        # Reset button
        reset_btn = tk.Button(
            btn_frame,
            text="🔄 Reset to Defaults",
            font=("Arial", 12),
            bg="#E74C3C",
            fg="white",
            activebackground="#C0392B",
            activeforeground="white",
            padx=15,
            pady=8,
            command=self.reset_to_defaults
        )
        reset_btn.pack(side=tk.LEFT, padx=10)
        
        # Back button
        back_btn = tk.Button(
            btn_frame,
            text="⬅️ Back to Lobby",
            font=("Arial", 12),
            bg="#95A5A6",
            fg="white",
            activebackground="#7F8C8D",
            activeforeground="white",
            padx=15,
            pady=8,
            command=self.on_back
        )
        back_btn.pack(side=tk.LEFT, padx=10)
    
    def on_theme_changed(self):
        """Xử lý khi theme thay đổi"""
        theme = self.theme_var.get()
        self.appearance_settings.set('board_theme', theme)
        self.draw_preview()
    
    def on_piece_style_changed(self):
        """Xử lý khi piece style thay đổi"""
        style = self.piece_style_var.get()
        self.appearance_settings.set('piece_style', style)
        self.draw_preview()
    
    def on_display_option_changed(self):
        """Xử lý khi display option thay đổi"""
        self.appearance_settings.set('show_coordinates', self.show_coords_var.get())
        self.appearance_settings.set('show_legal_moves', self.show_legal_var.get())
        self.draw_preview()
    
    def reset_to_defaults(self):
        """Reset về default settings"""
        self.appearance_settings.reset_to_defaults()
        
        # Update UI
        self.theme_var.set(self.appearance_settings.get('board_theme'))
        self.piece_style_var.set(self.appearance_settings.get('piece_style'))
        self.show_coords_var.set(self.appearance_settings.get('show_coordinates'))
        self.show_legal_var.set(self.appearance_settings.get('show_legal_moves'))
        
        self.draw_preview()
    
    def show(self):
        """Hiển thị screen"""
        self.frame.pack(fill=tk.BOTH, expand=True)
        self.draw_preview()
        # Reset scroll to top when showing
        self.canvas.yview_moveto(0)
    
    def hide(self):
        """Ẩn screen"""
        self.frame.pack_forget()
        # Unbind mousewheel when hiding
        self.canvas.unbind_all("<MouseWheel>")
