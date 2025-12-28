#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Login/Signup Screen
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading


class LoginScreen:
    """Màn hình đăng nhập và đăng ký"""
    
    def __init__(self, root, client, on_login_success):
        self.root = root
        self.client = client
        self.on_login_success = on_login_success
        
        # Main frame
        self.frame = tk.Frame(root, bg='#34495E')
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup login UI"""
        # Left side - Decorative
        left_frame = tk.Frame(self.frame, bg='#2C3E50', width=400)
        left_frame.pack(side='left', fill='both', expand=True)
        left_frame.pack_propagate(False)
        
        # Logo
        tk.Label(left_frame, text="♔", font=("Arial", 120), 
                fg='#ECF0F1', bg='#2C3E50').pack(pady=80)
        
        tk.Label(left_frame, text="Network Chess", 
                font=("Arial", 28, "bold"), 
                fg='#ECF0F1', bg='#2C3E50').pack()
        
        tk.Label(left_frame, text="Play chess online with friends", 
                font=("Arial", 12), 
                fg='#95A5A6', bg='#2C3E50').pack(pady=10)
        
        # Right side - Login form
        right_frame = tk.Frame(self.frame, bg='#ECF0F1')
        right_frame.pack(side='left', fill='both', expand=True)
        
        # Form container
        form_frame = tk.Frame(right_frame, bg='#ECF0F1')
        form_frame.pack(expand=True)
        
        # Title
        tk.Label(form_frame, text="Welcome Back!", 
                font=("Arial", 24, "bold"), 
                fg='#2C3E50', bg='#ECF0F1').pack(pady=(0, 10))
        
        tk.Label(form_frame, text="Login to continue", 
                font=("Arial", 11), 
                fg='#7F8C8D', bg='#ECF0F1').pack(pady=(0, 30))
        
        # Connection status
        self.status_frame = tk.Frame(form_frame, bg='#ECF0F1')
        self.status_frame.pack(pady=10)
        
        self.status_indicator = tk.Label(self.status_frame, text="●", 
                                         font=("Arial", 16), 
                                         fg='red', bg='#ECF0F1')
        self.status_indicator.pack(side='left', padx=5)
        
        self.status_label = tk.Label(self.status_frame, text="Disconnected", 
                                     font=("Arial", 10), 
                                     fg='#7F8C8D', bg='#ECF0F1')
        self.status_label.pack(side='left')
        
        # Server connection
        server_frame = tk.Frame(form_frame, bg='#ECF0F1')
        server_frame.pack(pady=10, fill='x', padx=50)
        
        tk.Label(server_frame, text="Server:", 
                font=("Arial", 10), 
                fg='#2C3E50', bg='#ECF0F1').pack(anchor='w')
        
        self.server_entry = tk.Entry(server_frame, font=("Arial", 11), 
                                     width=30, relief='solid', bd=1)
        self.server_entry.insert(0, "127.0.0.1:5001")
        self.server_entry.pack(fill='x', pady=5)
        
        self.connect_btn = tk.Button(server_frame, text="Connect to Server", 
                                     command=self.do_connect,
                                     bg='#3498DB', fg='white', 
                                     font=("Arial", 10, "bold"),
                                     relief='flat', cursor='hand2',
                                     activebackground='#2980B9')
        self.connect_btn.pack(fill='x', pady=5)
        
        # Separator
        ttk.Separator(form_frame, orient='horizontal').pack(fill='x', 
                                                            padx=50, pady=20)
        
        # Username
        input_frame1 = tk.Frame(form_frame, bg='#ECF0F1')
        input_frame1.pack(pady=10, fill='x', padx=50)
        
        tk.Label(input_frame1, text="Username", 
                font=("Arial", 10), 
                fg='#2C3E50', bg='#ECF0F1').pack(anchor='w')
        
        self.username_entry = tk.Entry(input_frame1, font=("Arial", 12), 
                                       width=30, relief='solid', bd=1)
        self.username_entry.pack(fill='x', pady=5, ipady=5)
        
        # Password
        input_frame2 = tk.Frame(form_frame, bg='#ECF0F1')
        input_frame2.pack(pady=10, fill='x', padx=50)
        
        tk.Label(input_frame2, text="Password", 
                font=("Arial", 10), 
                fg='#2C3E50', bg='#ECF0F1').pack(anchor='w')
        
        self.password_entry = tk.Entry(input_frame2, font=("Arial", 12), 
                                       show='●', width=30, 
                                       relief='solid', bd=1)
        self.password_entry.pack(fill='x', pady=5, ipady=5)
        
        # Email (for register)
        self.email_frame = tk.Frame(form_frame, bg='#ECF0F1')
        
        tk.Label(self.email_frame, text="Email (for registration)", 
                font=("Arial", 10), 
                fg='#2C3E50', bg='#ECF0F1').pack(anchor='w')
        
        self.email_entry = tk.Entry(self.email_frame, font=("Arial", 12), 
                                    width=30, relief='solid', bd=1)
        self.email_entry.pack(fill='x', pady=5, ipady=5)
        
        # Buttons
        btn_frame = tk.Frame(form_frame, bg='#ECF0F1')
        btn_frame.pack(pady=20, fill='x', padx=50)
        
        self.login_btn = tk.Button(btn_frame, text="Login", 
                                   command=self.do_login,
                                   bg='#27AE60', fg='white', 
                                   font=("Arial", 12, "bold"),
                                   relief='flat', cursor='hand2',
                                   activebackground='#229954')
        self.login_btn.pack(fill='x', pady=5, ipady=8)
        
        # Toggle to register
        toggle_frame = tk.Frame(form_frame, bg='#ECF0F1')
        toggle_frame.pack(pady=10)
        
        tk.Label(toggle_frame, text="Don't have an account?", 
                font=("Arial", 9), 
                fg='#7F8C8D', bg='#ECF0F1').pack(side='left')
        
        self.toggle_btn = tk.Button(toggle_frame, text="Sign Up", 
                                    command=self.toggle_mode,
                                    fg='#3498DB', bg='#ECF0F1',
                                    font=("Arial", 9, "bold"),
                                    relief='flat', cursor='hand2',
                                    activebackground='#ECF0F1',
                                    bd=0)
        self.toggle_btn.pack(side='left', padx=5)
        
        # Mode flag
        self.is_login_mode = True
    
    def toggle_mode(self):
        """Toggle between login and register mode"""
        self.is_login_mode = not self.is_login_mode
        
        if self.is_login_mode:
            # Login mode
            self.login_btn.config(text="Login", bg='#27AE60', 
                                 activebackground='#229954')
            self.toggle_btn.config(text="Sign Up")
            self.email_frame.pack_forget()
        else:
            # Register mode
            self.login_btn.config(text="Register", bg='#E74C3C',
                                 activebackground='#C0392B')
            self.toggle_btn.config(text="Login")
            self.email_frame.pack(pady=10, fill='x', padx=50)
    
    def do_connect(self):
        """Connect to server"""
        if self.client.connected:
            messagebox.showinfo("Info", "Already connected")
            return
        
        server_addr = self.server_entry.get().split(':')
        host = server_addr[0]
        port = int(server_addr[1]) if len(server_addr) > 1 else 5001
        
        self.client.host = host
        self.client.port = port
        
        if self.client.connect():
            self.status_indicator.config(fg='green')
            self.status_label.config(text="Connected")
            self.connect_btn.config(state='disabled', bg='#95A5A6')
            
            # Start listening thread
            threading.Thread(target=self.client.listen_loop, daemon=True).start()
            
            messagebox.showinfo("Connected", "Connected to server successfully!")
        else:
            messagebox.showerror("Error", "Failed to connect to server")
    
    def do_login(self):
        """Login or register"""
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showwarning("Warning", "Please enter username and password")
            return
        
        if not self.client.connected:
            messagebox.showwarning("Warning", "Please connect to server first")
            return
        
        if self.is_login_mode:
            # Login
            self.client.set_callback('LOGIN_RESPONSE', self.on_login_response)
            self.client.login(username, password)
        else:
            # Register
            email = self.email_entry.get()
            if not email:
                messagebox.showwarning("Warning", "Please enter email")
                return
            
            self.client.set_callback('REGISTER_RESPONSE', self.on_register_response)
            self.client.register(username, password, email)
    
    def on_login_response(self, msg):
        """Handle login response"""
        if msg.get('success'):
            self.client.session_token = msg.get('session_token')
            self.client.username = msg.get('username')
            elo = msg.get('elo', 1200)
            
            messagebox.showinfo("Success", f"Welcome {self.client.username}!\nELO: {elo}")
            self.on_login_success(elo)
        else:
            error = msg.get('message', 'Login failed')
            messagebox.showerror("Login Failed", error)
    
    def on_register_response(self, msg):
        """Handle register response"""
        if msg.get('success'):
            messagebox.showinfo("Success", "Registration successful! Please login.")
            self.toggle_mode()
        else:
            error = msg.get('message', 'Registration failed')
            messagebox.showerror("Registration Failed", error)
    
    def show(self):
        """Show login screen"""
        self.frame.pack(fill='both', expand=True)
    
    def hide(self):
        """Hide login screen"""
        self.frame.pack_forget()
