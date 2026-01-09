#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Protocol Payload Schemas - Typed dataclasses for message payloads
Synchronized with server protocol specification
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


# ============== Authentication Payloads ==============

@dataclass
class LoginPayload:
    """Payload for login request"""
    username: str
    password: str


@dataclass
class LoginResponsePayload:
    """Payload for login response"""
    user_id: int
    elo: int
    username: Optional[str] = None


@dataclass
class RegisterPayload:
    """Payload for registration request"""
    username: str
    password: str
    email: Optional[str] = None


@dataclass
class RegisterResponsePayload:
    """Payload for registration response"""
    user_id: Optional[int] = None
    message: Optional[str] = None


# ============== Game/Match Payloads ==============

@dataclass
class MatchStartPayload:
    """Payload when match starts"""
    game_id: int
    opponent_id: int
    opponent_name: str
    your_color: str  # "white" or "black"
    opponent_elo: int
    time_control: str  # e.g., "10+0"
    initial_fen: Optional[str] = None
    is_rematch: bool = False


@dataclass
class MovePayload:
    """Payload for chess move"""
    from_pos: str  # e.g., "e2"
    to_pos: str    # e.g., "e4"
    game_id: Optional[int] = None


@dataclass
class MoveResponsePayload:
    """Payload for move acknowledgment/update"""
    success: bool
    fen: Optional[str] = None
    next_fen: Optional[str] = None
    from_pos: Optional[str] = None
    to_pos: Optional[str] = None
    white_time: Optional[float] = None
    black_time: Optional[float] = None
    last_move: Optional[Dict[str, str]] = None
    message: Optional[str] = None


@dataclass
class GameEndPayload:
    """Payload when game ends"""
    result: str  # "win", "loss", "draw"
    reason: str
    new_elo: int
    winner: Optional[str] = None
    loser: Optional[str] = None
    elo_change: Optional[int] = None


# ============== Challenge Payloads ==============

@dataclass
class ChallengePayload:
    """Payload for sending challenge"""
    target_username: str
    mode: str = "RAPID"  # BLITZ, RAPID, CLASSICAL


@dataclass
class ChallengeNotifyPayload:
    """Payload when receiving challenge"""
    challenger_id: int
    challenger_username: str
    mode: str
    from_id: Optional[int] = None  # Alias for challenger_id


@dataclass
class AcceptChallengePayload:
    """Payload for accepting challenge"""
    challenger_username: str
    mode: str = "RAPID"


# ============== Rematch Payloads ==============

@dataclass
class RematchRequestPayload:
    """Payload for rematch request"""
    game_id: int
    requester_id: Optional[int] = None


@dataclass
class RematchResponsePayload:
    """Payload for rematch accept/decline"""
    game_id: int
    accepted: bool


# ============== Lobby/Players Payloads ==============

@dataclass
class PlayerInfo:
    """Individual player information"""
    username: str
    elo: int
    player_id: Optional[int] = None
    status: str = "online"


@dataclass
class LobbyListPayload:
    """Payload for lobby player list"""
    players: List[PlayerInfo] = field(default_factory=list)


@dataclass
class LeaderboardEntry:
    """Individual leaderboard entry"""
    rank: int
    username: str
    elo: int
    wins: int
    losses: int
    draws: int


@dataclass
class LeaderboardPayload:
    """Payload for leaderboard"""
    leaderboard: List[LeaderboardEntry] = field(default_factory=list)


# ============== Draw Offer Payloads ==============

@dataclass
class DrawOfferPayload:
    """Payload for draw offer"""
    game_id: int
    from_player: Optional[str] = None


# ============== Emoji/Chat Payloads ==============

@dataclass
class EmojiPayload:
    """Payload for emoji message"""
    emoji: str
    sender: str
    from_player: Optional[str] = None  # Alias


# ============== Error Payloads ==============

@dataclass
class ErrorPayload:
    """Payload for error messages"""
    error: str
    reason: Optional[str] = None
    message: Optional[str] = None


# ============== Helper Functions ==============

def dict_to_dataclass(data_class, data: Dict[str, Any]):
    """
    Convert dictionary to dataclass instance
    
    Args:
        data_class: The dataclass type to convert to
        data: Dictionary with payload data
        
    Returns:
        Instance of data_class with fields populated from data
        
    Example:
        login = dict_to_dataclass(LoginPayload, {'username': 'player1', 'password': 'pass'})
    """
    if not isinstance(data, dict):
        return None
    
    try:
        # Get field names from dataclass
        field_names = {f.name for f in data_class.__dataclass_fields__.values()}
        # Filter dict to only include valid fields
        filtered_data = {k: v for k, v in data.items() if k in field_names}
        return data_class(**filtered_data)
    except (TypeError, KeyError) as e:
        print(f"Error converting dict to {data_class.__name__}: {e}")
        return None


def safe_get_payload(msg: Dict[str, Any], payload_class):
    """
    Safely extract and convert payload from message
    
    Args:
        msg: Message dictionary
        payload_class: Dataclass type for payload
        
    Returns:
        Instance of payload_class or None if conversion fails
        
    Example:
        payload = safe_get_payload(msg, LoginResponsePayload)
        if payload:
            print(f"ELO: {payload.elo}")
    """
    payload_dict = msg.get('payload', {})
    if not isinstance(payload_dict, dict):
        return None
    return dict_to_dataclass(payload_class, payload_dict)


def safe_get_players(msg: Dict[str, Any]) -> List[PlayerInfo]:
    """
    Extract and convert player list from lobby message
    
    Args:
        msg: Message dictionary containing players
        
    Returns:
        List of PlayerInfo instances
    """
    payload = msg.get('payload', {})
    players_data = payload.get('players', [])
    
    players = []
    for player_data in players_data:
        if isinstance(player_data, str):
            # Simple username string
            players.append(PlayerInfo(username=player_data, elo=1200))
        elif isinstance(player_data, dict):
            # Full player dict
            player = dict_to_dataclass(PlayerInfo, player_data)
            if player:
                players.append(player)
    
    return players
