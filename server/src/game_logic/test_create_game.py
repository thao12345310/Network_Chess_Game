#!/usr/bin/env python3
"""Test create_game functionality"""
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db_handler import create_game

# Test create_game
try:
    print("Testing create_game with white_id=2, black_id=1, mode='RAPID'")
    game_id = create_game(2, 1, 'RAPID')
    print(f"SUCCESS! Game created with ID: {game_id}")
except Exception as e:
    print(f"FAILED! Error: {e}")
    import traceback
    traceback.print_exc()
