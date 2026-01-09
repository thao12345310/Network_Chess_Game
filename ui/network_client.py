#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python binding for C++ Chess Client using ctypes
Linux only version
"""

import ctypes
import json
import threading
from pathlib import Path
from protocol_constants import MessageType


# Linux shared library name
LIB_NAME = 'libchessclient.so'


class ChessClient:
    """Python wrapper for C++ GameClient using ctypes"""
    
    def __init__(self, host='127.0.0.1', port=5001):
        self.host = host
        self.port = port
        self.handle = None
        self.connected = False
        self.username = None
        self.callbacks = {}
        
        # Load shared library
        lib_path = Path(__file__).parent / LIB_NAME
        if not lib_path.exists():
            raise FileNotFoundError(f"C++ client library not found: {lib_path}\nPlease build C++ client first: cd client && make && make install")
        
        self.lib = ctypes.CDLL(str(lib_path))
        self._setup_function_signatures()
        
    def _setup_function_signatures(self):
        """Define C function signatures"""
        lib = self.lib
        
        # Callback types
        self.MessageCallbackType = ctypes.CFUNCTYPE(None, ctypes.c_char_p)
        self.ErrorCallbackType = ctypes.CFUNCTYPE(None, ctypes.c_char_p)
        
        # Client lifecycle
        lib.client_create.argtypes = [ctypes.c_char_p, ctypes.c_int]
        lib.client_create.restype = ctypes.c_void_p
        
        lib.client_destroy.argtypes = [ctypes.c_void_p]
        lib.client_destroy.restype = None
        
        lib.client_connect.argtypes = [ctypes.c_void_p]
        lib.client_connect.restype = ctypes.c_int
        
        lib.client_disconnect.argtypes = [ctypes.c_void_p]
        lib.client_disconnect.restype = None
        
        # Callbacks
        lib.client_set_login_callback.argtypes = [ctypes.c_void_p, self.MessageCallbackType]
        lib.client_set_login_callback.restype = None
        
        lib.client_set_game_update_callback.argtypes = [ctypes.c_void_p, self.MessageCallbackType]
        lib.client_set_game_update_callback.restype = None
        
        lib.client_set_player_list_callback.argtypes = [ctypes.c_void_p, self.MessageCallbackType]
        lib.client_set_player_list_callback.restype = None
        
        lib.client_set_challenge_callback.argtypes = [ctypes.c_void_p, self.MessageCallbackType]
        lib.client_set_challenge_callback.restype = None
        
        lib.client_set_error_callback.argtypes = [ctypes.c_void_p, self.ErrorCallbackType]
        lib.client_set_error_callback.restype = None
        
        # Actions
        lib.client_login.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p]
        lib.client_login.restype = ctypes.c_int
        
        lib.client_register.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p]
        lib.client_register.restype = ctypes.c_int
        
        lib.client_request_player_list.argtypes = [ctypes.c_void_p]
        lib.client_request_player_list.restype = ctypes.c_int
        
        lib.client_send_move.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p]
        lib.client_send_move.restype = ctypes.c_int
        
        lib.client_get_username.argtypes = [ctypes.c_void_p]
        lib.client_get_username.restype = ctypes.c_char_p
        
        lib.client_resign.argtypes = [ctypes.c_void_p]
        lib.client_resign.restype = ctypes.c_int
        
        lib.client_offer_draw.argtypes = [ctypes.c_void_p]
        lib.client_offer_draw.restype = ctypes.c_int
        
        lib.client_accept_draw.argtypes = [ctypes.c_void_p]
        lib.client_accept_draw.restype = ctypes.c_int
        
        lib.client_decline_draw.argtypes = [ctypes.c_void_p]
        lib.client_decline_draw.restype = ctypes.c_int
        
        # Challenge functions
        lib.client_send_challenge.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p]
        lib.client_send_challenge.restype = ctypes.c_int
        
        lib.client_accept_challenge.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p]
        lib.client_accept_challenge.restype = ctypes.c_int

        # Lobby functions
        lib.client_join_lobby.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        lib.client_join_lobby.restype = ctypes.c_int
        
        # Rematch functions
        lib.client_request_rematch.argtypes = [ctypes.c_void_p]
        lib.client_request_rematch.restype = ctypes.c_int
        
        lib.client_accept_rematch.argtypes = [ctypes.c_void_p]
        lib.client_accept_rematch.restype = ctypes.c_int
        
        lib.client_decline_rematch.argtypes = [ctypes.c_void_p]
        lib.client_decline_rematch.restype = ctypes.c_int

        lib.client_request_leaderboard.argtypes = [ctypes.c_void_p]
        lib.client_request_leaderboard.restype = ctypes.c_int
        
    def connect(self):
        """Connect to server"""
        try:
            # Create client handle
            self.handle = self.lib.client_create(
                self.host.encode('utf-8'),
                self.port
            )
            
            if not self.handle:
                return False
            
            # Setup callbacks
            self._setup_callbacks()
            
            # Connect
            result = self.lib.client_connect(self.handle)
            self.connected = (result == 1)
            return self.connected
        except Exception as e:
            print(f"Connection error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from server"""
        if self.handle:
            self.lib.client_disconnect(self.handle)
            self.lib.client_destroy(self.handle)
            self.handle = None
        self.connected = False
    
    def _setup_callbacks(self):
        """Setup C++ callbacks"""
        # Keep references to prevent garbage collection
        self._cb_login = self.MessageCallbackType(self._on_login_callback)
        self._cb_game_update = self.MessageCallbackType(self._on_game_update_callback)
        self._cb_player_list = self.MessageCallbackType(self._on_player_list_callback)
        self._cb_challenge = self.MessageCallbackType(self._on_challenge_callback)
        self._cb_error = self.ErrorCallbackType(self._on_error_callback)
        
        self.lib.client_set_login_callback(self.handle, self._cb_login)
        self.lib.client_set_game_update_callback(self.handle, self._cb_game_update)
        self.lib.client_set_player_list_callback(self.handle, self._cb_player_list)
        self.lib.client_set_challenge_callback(self.handle, self._cb_challenge)
        self.lib.client_set_error_callback(self.handle, self._cb_error)
    
    def _on_login_callback(self, json_msg):
        """Handle login response from C++"""
        try:
            if json_msg is None:
                print("ERROR: json_msg is None in login callback")
                return
            
            print(f"DEBUG: Received login callback: {json_msg}")
            msg = json.loads(json_msg.decode('utf-8'))
            print(f"DEBUG: Parsed message: {msg}")
            msg_type = msg.get('messageType', '')
            print(f"DEBUG: Message type: {msg_type}")
            
            # Handle both login and register responses
            if msg_type in self.callbacks:
                self.callbacks[msg_type](msg)
            elif MessageType.AUTH_LOGIN_ACK in self.callbacks and 'AUTH' in msg_type:
                self.callbacks[MessageType.AUTH_LOGIN_ACK](msg)
            elif MessageType.AUTH_REGISTER_ACK in self.callbacks and 'AUTH' in msg_type:
                self.callbacks[MessageType.AUTH_REGISTER_ACK](msg)
            else:
                print(f"WARNING: No callback registered for message type: {msg_type}")
        except Exception as e:
            import traceback
            print(f"Login callback error: {e}")
            print(f"Traceback: {traceback.format_exc()}")
    
    def _on_game_update_callback(self, json_msg):
        """Handle game update from C++"""
        try:
            msg = json.loads(json_msg.decode('utf-8'))
            msg_type = msg.get('messageType', '')
            print(f"DEBUG: Game update received - type: {msg_type}")
            if msg_type in self.callbacks:
                print(f"DEBUG: Calling callback for {msg_type}")
                self.callbacks[msg_type](msg)
            else:
                print(f"WARNING: No callback registered for game update: {msg_type}")
        except Exception as e:
            import traceback
            print(f"Game update callback error: {e}")
            print(f"Traceback: {traceback.format_exc()}")
    
    def _on_player_list_callback(self, json_msg):
        """Handle player list from C++"""
        try:
            msg = json.loads(json_msg.decode('utf-8'))
            msg_type = msg.get('messageType', '')
            
            if msg_type == MessageType.LOBBY_LIST and MessageType.LOBBY_LIST in self.callbacks:
                self.callbacks[MessageType.LOBBY_LIST](msg)
            elif msg_type == MessageType.LEADERBOARD and MessageType.LEADERBOARD in self.callbacks:
                self.callbacks[MessageType.LEADERBOARD](msg.get('payload', {}))
        except Exception as e:
            print(f"Player list callback error: {e}")
    
    def _on_challenge_callback(self, json_msg):
        """Handle challenge notification from C++"""
        try:
            msg = json.loads(json_msg.decode('utf-8'))
            msg_type = msg.get('messageType', '')
            print(f"DEBUG: Challenge callback received: {msg_type}")
            if msg_type in self.callbacks:
                self.callbacks[msg_type](msg)
            elif MessageType.CHALLENGE_NOTIFY in self.callbacks:
                self.callbacks[MessageType.CHALLENGE_NOTIFY](msg)
        except Exception as e:
            print(f"Challenge callback error: {e}")
    
    def _on_error_callback(self, error_msg):
        """Handle error from C++"""
        try:
            error_str = error_msg.decode('utf-8')
            if MessageType.ERROR in self.callbacks:
                self.callbacks[MessageType.ERROR]({'error': error_str})
            print(f"C++ Client Error: {error_str}")
        except Exception as e:
            print(f"Error callback error: {e}")
    
    def set_callback(self, msg_type, callback):
        """Register callback for message type"""
        self.callbacks[msg_type] = callback
    
    def login(self, username, password):
        """Login to server"""
        if not self.handle:
            return False
        self.username = username
        result = self.lib.client_login(
            self.handle,
            username.encode('utf-8'),
            password.encode('utf-8')
        )
        return result == 1
    
    def register(self, username, password):
        """Register new account"""
        if not self.handle:
            return False
        result = self.lib.client_register(
            self.handle,
            username.encode('utf-8'),
            password.encode('utf-8')
        )
        return result == 1
    
    def get_player_list(self):
        """Request player list"""
        if not self.handle:
            return False
        result = self.lib.client_request_player_list(self.handle)
        return result == 1
    
    def make_move(self, game_id, from_pos, to_pos):
        """Make a chess move"""
        if not self.handle:
            return False
        result = self.lib.client_send_move(
            self.handle,
            from_pos.encode('utf-8'),
            to_pos.encode('utf-8')
        )
        return result == 1
    
    def random_match(self, mode="RAPID"):
        """Find random match"""
        if not self.handle:
            return False
        # Call with mode
        result = self.lib.client_join_lobby(self.handle, mode.encode('utf-8'))
        return result == 1
    
    def logout(self):
        """Logout - send logout message then disconnect"""
        if self.handle:
            # Send logout message to server first
            self.lib.client_logout(self.handle)
            # Small delay to ensure message is sent
            import time
            time.sleep(0.1)
        self.disconnect()
        return True
    
    def resign(self, game_id):
        """Resign from game"""
        if not self.handle:
            return False
        return self.lib.client_resign(self.handle) == 1
    
    def offer_draw(self, game_id):
        """Offer draw"""
        if not self.handle:
            return False
        return self.lib.client_offer_draw(self.handle) == 1
    
    def accept_draw(self, game_id):
        """Accept draw offer"""
        if not self.handle:
            return False
        return self.lib.client_accept_draw(self.handle) == 1
    
    def decline_draw(self, game_id):
        """Decline draw offer"""
        if not self.handle:
            return False
        return self.lib.client_decline_draw(self.handle) == 1
    
    def request_rematch(self, game_id):
        """Request rematch after game ends"""
        if not self.handle:
            return False
        return self.lib.client_request_rematch(self.handle) == 1
    
    def accept_rematch(self, game_id):
        """Accept rematch request"""
        if not self.handle:
            return False
        return self.lib.client_accept_rematch(self.handle) == 1
    
    def decline_rematch(self, game_id):
        """Decline rematch request"""
        if not self.handle:
            return False
        return self.lib.client_decline_rematch(self.handle) == 1
    
    # Challenge methods
    def send_challenge(self, opponent, mode="RAPID"):
        """Send challenge to specific player"""
        if not self.handle:
            return False
        result = self.lib.client_send_challenge(
            self.handle,
            opponent.encode('utf-8'),
            mode.encode('utf-8')
        )
        return result == 1
    
    def accept_challenge(self, challenger_id, mode="RAPID"):
        """Accept challenge from a player"""
        if not self.handle:
            return False
        result = self.lib.client_accept_challenge(
            self.handle,
            str(challenger_id).encode('utf-8'),
            mode.encode('utf-8')
        )
        return result == 1
    
    def reject_challenge(self, challenger):
        """Reject challenge - not sending accept"""
        pass  # Server handles rejection if no accept is sent
    
    def get_leaderboard(self):
        """Request leaderboard data"""
        if not self.handle:
            return False
        return self.lib.client_request_leaderboard(self.handle) == 1
    
    def get_player_stats(self, username=None):
        """Not implemented yet"""
        pass
