#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for Game History & Replay feature
"""

import sys
import json
import subprocess
from pathlib import Path

# Path to logic_wrapper.py
LOGIC_WRAPPER = Path(__file__).parent / 'server' / 'src' / 'game_logic' / 'logic_wrapper.py'


def call_logic(action, **params):
    """Call logic_wrapper.py with given action and parameters"""
    request = {"action": action, **params}
    
    try:
        result = subprocess.run(
            [sys.executable, str(LOGIC_WRAPPER)],
            input=json.dumps(request),
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            print(f"Error: {result.stderr}")
            return None
    except Exception as e:
        print(f"Exception: {e}")
        return None


def test_get_game_history():
    """Test getting game history for a player"""
    print("=" * 60)
    print("TEST: Get Game History")
    print("=" * 60)
    
    # Test with player_id = 1 (adjust based on your database)
    player_id = 1
    
    print(f"\nGetting game history for player_id={player_id}...")
    response = call_logic("get_game_history", player_id=player_id)
    
    if response:
        print(f"\nStatus: {response.get('status')}")
        
        if response.get('status') == 'success':
            games = response.get('games', [])
            print(f"Found {len(games)} game(s)\n")
            
            for i, game in enumerate(games, 1):
                print(f"Game {i}:")
                print(f"  ID: {game.get('game_id')}")
                print(f"  Mode: {game.get('mode')}")
                print(f"  Opponent: {game.get('opponent_username')}")
                print(f"  Your Color: {game.get('player_color')}")
                print(f"  Result: {game.get('result')}")
                print(f"  Date: {game.get('end_time', '')[:16]}")
                print()
        else:
            print(f"Error: {response.get('message')}")
    else:
        print("Failed to get response")


def test_get_game_replay():
    """Test getting game details for replay"""
    print("=" * 60)
    print("TEST: Get Game Replay")
    print("=" * 60)
    
    # First get game history to find a game_id
    player_id = 1
    response = call_logic("get_game_history", player_id=player_id)
    
    if not response or response.get('status') != 'success':
        print("Cannot get game history to test replay")
        return
    
    games = response.get('games', [])
    if not games:
        print("No games found to test replay")
        return
    
    # Use the first game
    game_id = games[0].get('game_id')
    print(f"\nGetting replay data for game_id={game_id}...")
    
    response = call_logic("get_game_replay", game_id=game_id)
    
    if response:
        print(f"\nStatus: {response.get('status')}")
        
        if response.get('status') == 'success':
            game = response.get('game', {})
            print(f"\nGame Details:")
            print(f"  ID: {game.get('game_id')}")
            print(f"  Mode: {game.get('mode')}")
            print(f"  Status: {game.get('status')}")
            print(f"  White: {game.get('white_player', {}).get('username')} (ELO: {game.get('white_player', {}).get('elo')})")
            print(f"  Black: {game.get('black_player', {}).get('username')} (ELO: {game.get('black_player', {}).get('elo')})")
            print(f"  Start: {game.get('start_time', '')[:16]}")
            print(f"  End: {game.get('end_time', '')[:16]}")
            
            moves = game.get('moves', [])
            print(f"\n  Total Moves: {len(moves)}")
            
            if moves:
                print(f"\n  First 10 moves:")
                for i, move in enumerate(moves[:10], 1):
                    if i % 2 == 1:
                        print(f"    {(i+1)//2}. {move}", end=" ")
                    else:
                        print(move)
                
                if len(moves) > 10:
                    print(f"    ... and {len(moves) - 10} more moves")
        else:
            print(f"Error: {response.get('message')}")
    else:
        print("Failed to get response")


def test_create_sample_game():
    """Create a sample finished game for testing"""
    print("=" * 60)
    print("TEST: Create Sample Game")
    print("=" * 60)
    
    # This is just a helper to create test data
    # You would normally create games through actual gameplay
    
    print("\nTo create sample games, you can:")
    print("1. Play actual games through the UI")
    print("2. Or manually insert into database:")
    print("""
    INSERT INTO Game (white_id, black_id, mode, start_time, end_time, winner_id, status)
    VALUES (1, 2, 'RAPID', datetime('now'), datetime('now'), 1, 'FINISHED');
    
    -- Get the game_id from the insert
    INSERT INTO Move (game_id, player_id, move_notation)
    VALUES 
        (1, 1, 'e2e4'),
        (1, 2, 'e7e5'),
        (1, 1, 'g1f3'),
        (1, 2, 'b8c6');
    """)


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("GAME HISTORY & REPLAY FEATURE TESTS")
    print("=" * 60 + "\n")
    
    # Check if logic_wrapper exists
    if not LOGIC_WRAPPER.exists():
        print(f"ERROR: logic_wrapper.py not found at {LOGIC_WRAPPER}")
        return
    
    print(f"Using logic_wrapper at: {LOGIC_WRAPPER}\n")
    
    # Run tests
    test_get_game_history()
    print("\n")
    test_get_game_replay()
    print("\n")
    test_create_sample_game()
    
    print("\n" + "=" * 60)
    print("TESTS COMPLETED")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
