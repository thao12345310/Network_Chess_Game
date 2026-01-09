#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Protocol Constants - Message Types and Response Codes
Synchronized with server/src/Protocol.h
"""


class ResponseCode:
    """HTTP-style response codes"""
    SUCCESS = 200
    CREATED = 201
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    CONFLICT = 409
    SERVER_ERROR = 500


class MessageType:
    """Message type identifiers for client-server communication"""
    
    # Authentication
    AUTH_REGISTER_REQ = "AUTH_REGISTER_REQ"
    AUTH_REGISTER_ACK = "AUTH_REGISTER_ACK"
    AUTH_LOGIN_REQ = "AUTH_LOGIN_REQ"
    AUTH_LOGIN_ACK = "AUTH_LOGIN_ACK"
    AUTH_LOGOUT_REQ = "AUTH_LOGOUT_REQ"
    AUTH_LOGOUT_ACK = "AUTH_LOGOUT_ACK"
    
    # Lobby
    LOBBY_LIST = "LOBBY_LIST"
    
    # Matchmaking
    MATCH_FIND_REQ = "MATCH_FIND_REQ"
    MATCH_CANCEL_REQ = "MATCH_CANCEL_REQ"
    MATCH_CANCEL_ACK = "MATCH_CANCEL_ACK"
    MATCH_START = "MATCH_START"
    
    # Gameplay
    MOVE_REQ = "MOVE_REQ"
    MOVE_ACK = "MOVE_ACK"
    MOVE_UPDATE = "MOVE_UPDATE"
    
    # Interaction
    EMOJI_SEND = "EMOJI_SEND"
    EMOJI_UPDATE = "EMOJI_UPDATE"
    
    # Game Actions
    GAME_RESIGN = "GAME_RESIGN"
    GAME_END = "GAME_END"
    DRAW_OFFER = "DRAW_OFFER"
    DRAW_OFFER_ACK = "DRAW_OFFER_ACK"
    DRAW_OFFER_NOTIFY = "DRAW_OFFER_NOTIFY"
    DRAW_ACCEPT = "DRAW_ACCEPT"
    DRAW_DECLINE = "DRAW_DECLINE"
    
    # Rematch
    REMATCH_REQUEST = "REMATCH_REQUEST"
    REMATCH_REQUEST_ACK = "REMATCH_REQUEST_ACK"
    REMATCH_REQUEST_NOTIFY = "REMATCH_REQUEST_NOTIFY"
    REMATCH_ACCEPT = "REMATCH_ACCEPT"
    REMATCH_DECLINE = "REMATCH_DECLINE"
    REMATCH_DECLINED_NOTIFY = "REMATCH_DECLINED_NOTIFY"
    
    # Errors
    ERROR = "ERROR"
    
    # Challenge
    CHALLENGE_REQ = "CHALLENGE_REQ"
    CHALLENGE_RESP = "CHALLENGE_RESP"
    CHALLENGE_NOTIFY = "CHALLENGE_NOTIFY"
    
    # Leaderboard
    LEADERBOARD = "LEADERBOARD"


class PayloadFields:
    """Common payload field names - synchronized with server protocol"""
    
    # User/Auth fields
    USER_ID = "user_id"
    USERNAME = "username"
    PASSWORD = "password"
    EMAIL = "email"
    ELO = "elo"
    NEW_ELO = "new_elo"
    
    # Game fields
    GAME_ID = "game_id"
    OPPONENT_NAME = "opponent_name"
    OPPONENT_ID = "opponent_id"
    YOUR_COLOR = "your_color"
    OPPONENT_ELO = "opponent_elo"
    TIME_CONTROL = "time_control"
    MODE = "mode"
    
    # Board state
    FEN = "fen"
    NEXT_FEN = "next_fen"
    INITIAL_FEN = "initial_fen"
    
    # Move fields
    FROM = "from"
    TO = "to"
    MOVE = "move"
    LAST_MOVE = "last_move"
    
    # Time fields
    WHITE_TIME = "white_time"
    BLACK_TIME = "black_time"
    
    # Game result
    RESULT = "result"  # "win", "loss", "draw"
    REASON = "reason"
    WINNER = "winner"
    LOSER = "loser"
    
    # Status/Error
    SUCCESS = "success"
    STATUS = "status"
    MESSAGE = "message"
    ERROR = "error"
    
    # Challenge fields
    CHALLENGER = "challenger"
    CHALLENGER_ID = "challenger_id"
    REQUESTER_ID = "requester_id"
    TARGET = "target"
    
    # Lobby/Players
    PLAYERS = "players"
    PLAYER_LIST = "player_list"
    
    # Leaderboard
    LEADERBOARD = "leaderboard"
    RANK = "rank"
    WINS = "wins"
    LOSSES = "losses"
    DRAWS = "draws"
    
    # Emoji
    EMOJI = "emoji"
    SENDER = "sender"


# Convenience functions
def is_error_response(msg):
    """Check if message is an error"""
    return msg.get('messageType') == MessageType.ERROR or msg.get('responseCode', 200) >= 400


def is_success_response(msg):
    """Check if message indicates success"""
    return msg.get('responseCode', 200) < 400


def get_payload(msg):
    """Safely extract payload from message"""
    return msg.get('payload', {}) if isinstance(msg.get('payload'), dict) else {}
