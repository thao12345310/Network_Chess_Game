#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TCP Network Client for Chess Game
"""

import socket
import json
from datetime import datetime


class ChessClient:
    """TCP Socket Client for Chess Game"""
    
    def __init__(self, host='127.0.0.1', port=5001):
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        self.session_token = None
        self.username = None
        self.game_id = None
        self.callbacks = {}
        
    def connect(self):
        """Connect to server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.connected = True
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from server"""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        self.connected = False
        self.socket = None
    
    def send_message(self, msg_dict):
        """Send JSON message to server"""
        if not self.connected:
            return False
        
        try:
            msg_json = json.dumps(msg_dict)
            msg_bytes = msg_json.encode('utf-8')
            # Send message length first (4 bytes)
            msg_len = len(msg_bytes)
            self.socket.sendall(msg_len.to_bytes(4, byteorder='big'))
            # Send actual message
            self.socket.sendall(msg_bytes)
            return True
        except Exception as e:
            print(f"Send error: {e}")
            return False
    
    def receive_message(self):
        """Receive JSON message from server"""
        try:
            # Read message length (4 bytes)
            len_bytes = self.socket.recv(4)
            if not len_bytes:
                return None
            msg_len = int.from_bytes(len_bytes, byteorder='big')
            
            # Read actual message
            msg_bytes = b''
            while len(msg_bytes) < msg_len:
                chunk = self.socket.recv(msg_len - len(msg_bytes))
                if not chunk:
                    return None
                msg_bytes += chunk
            
            msg_json = msg_bytes.decode('utf-8')
            return json.loads(msg_json)
        except Exception as e:
            print(f"Receive error: {e}")
            return None
    
    def listen_loop(self):
        """Listen for incoming messages"""
        while self.connected:
            msg = self.receive_message()
            if msg:
                self.handle_message(msg)
            else:
                self.connected = False
                break
    
    def handle_message(self, msg):
        """Handle received message"""
        msg_type = msg.get('type', '')
        if msg_type in self.callbacks:
            self.callbacks[msg_type](msg)
    
    def set_callback(self, msg_type, callback):
        """Set callback for message type"""
        self.callbacks[msg_type] = callback
    
    # Game actions
    def login(self, username, password):
        """Login to server"""
        return self.send_message({
            'type': 'LOGIN',
            'username': username,
            'password': password,
            'timestamp': int(datetime.now().timestamp())
        })
    
    def register(self, username, password, email):
        """Register new account"""
        return self.send_message({
            'type': 'REGISTER',
            'username': username,
            'password': password,
            'email': email,
            'timestamp': int(datetime.now().timestamp())
        })
    
    def logout(self):
        """Logout from server"""
        return self.send_message({
            'type': 'LOGOUT',
            'session_token': self.session_token
        })
    
    def get_player_list(self):
        """Get list of online players"""
        return self.send_message({
            'type': 'GET_PLAYERS',
            'session_token': self.session_token
        })
    
    def send_challenge(self, opponent):
        """Send challenge to opponent"""
        return self.send_message({
            'type': 'CHALLENGE',
            'session_token': self.session_token,
            'opponent': opponent
        })
    
    def accept_challenge(self, challenger):
        """Accept challenge"""
        return self.send_message({
            'type': 'ACCEPT_CHALLENGE',
            'session_token': self.session_token,
            'challenger': challenger
        })
    
    def reject_challenge(self, challenger):
        """Reject challenge"""
        return self.send_message({
            'type': 'REJECT_CHALLENGE',
            'session_token': self.session_token,
            'challenger': challenger
        })
    
    def random_match(self):
        """Find random opponent"""
        return self.send_message({
            'type': 'RANDOM_MATCH',
            'session_token': self.session_token
        })
    
    def get_leaderboard(self):
        """Get ELO leaderboard"""
        return self.send_message({
            'type': 'GET_LEADERBOARD',
            'session_token': self.session_token
        })
    
    def get_player_stats(self, username=None):
        """Get player statistics"""
        return self.send_message({
            'type': 'GET_STATS',
            'session_token': self.session_token,
            'username': username
        })
    
    def make_move(self, game_id, from_pos, to_pos):
        """Make a move"""
        return self.send_message({
            'type': 'MOVE',
            'game_id': game_id,
            'session_token': self.session_token,
            'from': from_pos,
            'to': to_pos,
            'timestamp': int(datetime.now().timestamp())
        })
    
    def resign(self, game_id):
        """Resign from game"""
        return self.send_message({
            'type': 'RESIGN',
            'game_id': game_id,
            'session_token': self.session_token
        })
    
    def offer_draw(self, game_id):
        """Offer draw"""
        return self.send_message({
            'type': 'OFFER_DRAW',
            'game_id': game_id,
            'session_token': self.session_token
        })
