"""
Connect 5 with Rotation - AI Players Module
Contains functions for AI players (GPT-4 and Claude)
"""
import json
import os
import random
import re
import sys

import anthropic
import openai

from board import board_to_string, is_valid_location, get_valid_moves, ROW_COUNT, COLUMN_COUNT, ROTATION_INTERVAL

# Set up OpenAI API key
try:
    # First try to read from environment variable
    api_key = os.getenv("OPENAI_API_KEY")
    
    # If not found in environment, try to read from .env file
    if api_key is None:
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                for line in f:
                    if line.startswith('export OPENAI_API_KEY='):
                        api_key = line.split('=')[1].strip().strip("'")
                        break
    
    if api_key is None:
        raise Exception("Could not find OpenAI API key")
        
    openai.api_key = api_key
except Exception as e:
    sys.exit(f"Error setting up OpenAI API key: {str(e)}")

# Set up Claude API
try:
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    if not anthropic_api_key:
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                for line in f:
                    if line.startswith('export ANTHROPIC_API_KEY='):
                        anthropic_api_key = line.split('=')[1].strip().strip("'")
                        break
    
    if not anthropic_api_key:
        raise Exception("Could not find Anthropic API key")
        
    anthropic_client = anthropic.Anthropic(api_key=anthropic_api_key)
except Exception as e:
    sys.exit(f"Error setting up Anthropic API key: {str(e)}")

# Game history to track moves
game_history = []

def get_random_valid_move(board, rotation_state):
    """Get a random valid move."""
    valid_moves = get_valid_moves(board, rotation_state)
    if valid_moves:
        return random.choice(valid_moves)
    return None

def get_move_from_gpt(board, player, turn_number, rotation_state=0):
    """
    Get a move from GPT (OpenAI) with improved context and game history.
    """
    board_str = board_to_string(board, rotation_state)
    
    # Get current dimensions
    ROWS, COLS = board.shape
    
    # Get valid moves (always columns with gravity pulling down)
    valid_columns = [col + 1 for col in range(COLS) if is_valid_location(board, col, rotation_state)]
    
    # Core rules explanation with rotation
    rules_summary = (
        "Rules: This is Connect 5 with rotation. Players take turns dropping pieces. "
        "A piece always falls downward (gravity pulls down). "
        "Every 6 moves (3 turns each player), the board rotates 90 degrees clockwise, and pieces fall to realign with gravity. "
        "The goal is to connect five of your pieces in a row horizontally, vertically, or diagonally."
    )
    
    # Provide the full game history as context
    history_str = ""
    if game_history:
        history_str = "Move history (format: turn_number-player-column):\n"
        history_str += "\n".join([f"{i+1}-{move['player']}-{move['column']}" for i, move in enumerate(game_history)])
        history_str += "\n\n"
    
    # Information about gravity
    current_gravity = "down"  # Gravity always pulls down
    next_rotation = (turn_number) % ROTATION_INTERVAL == 0
    
    prompt = (
        f"{rules_summary}\n\n"
        f"Current board state (Turn {turn_number}, Rotation: {rotation_state % 4}):\n{board_str}\n\n"
        f"{'Board will rotate after this move!' if next_rotation else ''}\n\n"
        f"{history_str}"
        f"Valid moves: {valid_columns}\n\n"
        f"You are playing as {'Player 1 (X)' if player == 1 else 'Player 2 (O)'}. "
        "Analyze the board and choose the best valid column to drop your piece. "
        "Respond with a JSON object containing a 'move' field with an integer value representing your chosen column number."
    )
    
    messages = [
        {
            "role": "system",
            "content": (
                "You are an expert Connect 5 AI. Analyze the current board state and choose the best move. "
                "Respond with a JSON object containing a 'move' field with an integer value from the valid moves provided."
            )
        },
        {"role": "user", "content": prompt}
    ]
    
    try:
        print("\n🤖 GPT-4 is thinking...")
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.5
        )
        
        # Parse the JSON response
        response_content = response.choices[0].message['content']
        print(f"🤖 GPT-4 response: {response_content}")
        
        response_json = json.loads(response_content)
        move = int(response_json['move']) - 1  # Convert to 0-indexed
        
        # Check if move is valid (column must be in valid range and have space)
        # Get current dimensions
        ROWS, COLS = board.shape
        
        if move not in range(COLS) or not is_valid_location(board, move, rotation_state):
            print(f"❌ GPT-4 suggested an invalid move: {move+1}. Valid moves are: {valid_columns}")
            print("Making a random valid move instead.")
            return get_random_valid_move(board, rotation_state)
            
        return move
    except Exception as e:
        print(f"❌ Error getting move from GPT-4: {str(e)}")
        print(f"Response content: {response.choices[0].message['content'] if 'response' in locals() else 'No response'}")
        print("Making a random valid move instead.")
        return get_random_valid_move(board, rotation_state)

def get_move_from_claude(board, player, turn_number, rotation_state=0):
    """
    Get a move from Claude (Anthropic) with improved context and game history.
    """
    board_str = board_to_string(board, rotation_state)
    
    # Get current dimensions
    ROWS, COLS = board.shape
    
    # Get valid moves (always columns with gravity pulling down)
    valid_columns = [col + 1 for col in range(COLS) if is_valid_location(board, col, rotation_state)]
    
    # Provide the full game history as context
    history_str = ""
    if game_history:
        history_str = "Move history (format: turn_number-player-column):\n"
        history_str += "\n".join([f"{i+1}-{move['player']}-{move['column']}" for i, move in enumerate(game_history)])
        history_str += "\n\n"
    
    # Information about gravity
    current_gravity = "down"  # Gravity always pulls down
    next_rotation = (turn_number) % ROTATION_INTERVAL == 0
    
    system_prompt = (
        "You are an expert Connect 5 AI. Analyze the current board state and choose the best move. "
        "Respond with a JSON object containing a 'move' field with the chosen column number from the valid moves provided."
    )
    
    user_prompt = (
        "Rules: This is Connect 5 with rotation. Players take turns dropping pieces. "
        "A piece always falls downward (gravity pulls down). "
        "Every 6 moves (3 turns each player), the board rotates 90 degrees clockwise, and pieces fall to realign with gravity. "
        "The goal is to connect five of your pieces in a row horizontally, vertically, or diagonally.\n\n"
        f"Current board state (Turn {turn_number}, Rotation: {rotation_state % 4}):\n{board_str}\n\n"
        f"{'Board will rotate after this move!' if next_rotation else ''}\n\n"
        f"{history_str}"
        f"Valid moves: {valid_columns}\n\n"
        f"You are playing as {'Player 1 (X)' if player == 1 else 'Player 2 (O)'}. "
        "Analyze the board and choose the best valid column to drop your piece. "
        "Respond with a JSON object containing a 'move' field with the chosen column number."
    )
    
    try:
        print("\n🤖 Claude is thinking...")
        message = anthropic_client.messages.create(
            model="claude-3-7-sonnet-latest",
            max_tokens=150,
            temperature=0.5,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        
        # Extract the move from the response
        response_content = message.content[0].text
        print(f"🤖 Claude response: {response_content}")
        
        # Use regex to find the JSON object
        json_match = re.search(r'({[\s\S]*?})', response_content)
        if not json_match:
            print(f"❌ Could not parse JSON from Claude's response: {response_content}")
            # Fallback to just finding the move number
            move_match = re.search(r'"move":\s*(\d+)', response_content)
            if not move_match:
                print("❌ Could not parse move number either.")
                print("Making a random valid move instead.")
                return get_random_valid_move(board, rotation_state)
            move = int(move_match.group(1)) - 1  # Convert to 0-indexed
        else:
            try:
                response_json = json.loads(json_match.group(1))
                move = int(response_json['move']) - 1  # Convert to 0-indexed
            except json.JSONDecodeError:
                print(f"❌ Invalid JSON from Claude: {json_match.group(1)}")
                # Fallback to just finding the move number
                move_match = re.search(r'"move":\s*(\d+)', response_content)
                if not move_match:
                    print("❌ Could not parse move number either.")
                    print("Making a random valid move instead.")
                    return get_random_valid_move(board, rotation_state)
                move = int(move_match.group(1)) - 1  # Convert to 0-indexed
        
        # Check if move is valid (column must be in valid range and have space)
        # Get current dimensions
        ROWS, COLS = board.shape
        
        if move not in range(COLS) or not is_valid_location(board, move, rotation_state):
            print(f"❌ Claude suggested an invalid move: {move+1}. Valid moves are: {valid_columns}")
            print("Making a random valid move instead.")
            return get_random_valid_move(board, rotation_state)
            
        return move
    except Exception as e:
        print(f"❌ Error getting move from Claude: {str(e)}")
        print("Making a random valid move instead.")
        return get_random_valid_move(board, rotation_state)