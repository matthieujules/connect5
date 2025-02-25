import json
import os
import re
import time

import anthropic
import numpy as np
import openai

from visualization import draw_board

# Constants from the original game
ROW_COUNT = 8
COLUMN_COUNT = 9

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
    raise Exception(f"Error setting up OpenAI API key: {str(e)}")

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
    raise Exception(f"Error setting up Anthropic API key: {str(e)}")

def create_board():
    return np.zeros((ROW_COUNT, COLUMN_COUNT), dtype=int)

def drop_piece(board, row, col, piece):
    board[row][col] = piece

def is_valid_location(board, col):
    return 0 <= col < COLUMN_COUNT and board[ROW_COUNT - 1][col] == 0

def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r
    return None

def winning_move(board, piece):
    # Horizontal
    for c in range(COLUMN_COUNT - 4):
        for r in range(ROW_COUNT):
            if all(board[r][c + i] == piece for i in range(5)):
                return True

    # Vertical
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT - 4):
            if all(board[r + i][c] == piece for i in range(5)):
                return True

    # Diagonal (positive slope)
    for c in range(COLUMN_COUNT - 4):
        for r in range(ROW_COUNT - 4):
            if all(board[r + i][c + i] == piece for i in range(5)):
                return True

    # Diagonal (negative slope)
    for c in range(COLUMN_COUNT - 4):
        for r in range(4, ROW_COUNT):
            if all(board[r - i][c + i] == piece for i in range(5)):
                return True

    return False

def board_to_string(board):
    """Convert the board to a string representation for the AI models."""
    symbols = {0: '.', 1: 'X', 2: 'O'}
    rows = []
    for r in range(ROW_COUNT-1, -1, -1):  # Flip board vertically for display
        row = ' '.join(symbols[board[r][c]] for c in range(COLUMN_COUNT))
        rows.append(row)
    # Add column numbers at the bottom
    rows.append(' '.join(str(i) for i in range(1, COLUMN_COUNT + 1)))
    return '\n'.join(rows)

# Track game history for context
game_history = []

def get_move_from_gpt(board, player, turn_number):
    """
    Get a move from GPT (OpenAI) with improved context and game history.
    """
    board_str = board_to_string(board)
    valid_columns = [col + 1 for col in range(COLUMN_COUNT) if is_valid_location(board, col)]
    
    # Core rules explanation
    rules_summary = (
        "Rules: This is Connect 5. Players take turns dropping pieces into columns. "
        "A piece falls to the lowest available space in that column. "
        "The goal is to connect five of your pieces in a row horizontally, vertically, or diagonally."
    )
    
    # Provide the full game history as context
    history_str = ""
    if game_history:
        history_str = "Move history (format: turn_number-player-column):\n"
        history_str += "\n".join([f"{i+1}-{move['player']}-{move['column']}" for i, move in enumerate(game_history)])
        history_str += "\n\n"
    
    prompt = (
        f"{rules_summary}\n\n"
        f"Current board state (Turn {turn_number}):\n{board_str}\n\n"
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
        
        if move not in range(COLUMN_COUNT) or not is_valid_location(board, move):
            print(f"❌ GPT-4 suggested an invalid move: {move+1}. Valid moves are: {valid_columns}")
            return None
            
        return move
    except Exception as e:
        print(f"❌ Error getting move from GPT-4: {str(e)}")
        print(f"Response content: {response.choices[0].message['content'] if 'response' in locals() else 'No response'}")
        return None

def get_move_from_claude(board, player, turn_number):
    """
    Get a move from Claude (Anthropic) with improved context and game history.
    """
    board_str = board_to_string(board)
    valid_columns = [col + 1 for col in range(COLUMN_COUNT) if is_valid_location(board, col)]
    
    # Provide the full game history as context
    history_str = ""
    if game_history:
        history_str = "Move history (format: turn_number-player-column):\n"
        history_str += "\n".join([f"{i+1}-{move['player']}-{move['column']}" for i, move in enumerate(game_history)])
        history_str += "\n\n"
    
    system_prompt = (
        "You are an expert Connect 5 AI. Analyze the current board state and choose the best move. "
        "Respond with a JSON object containing a 'move' field with the chosen column number from the valid moves provided."
    )
    
    user_prompt = (
        "Rules: This is Connect 5. Players take turns dropping pieces into columns. "
        "A piece falls to the lowest available space in that column. "
        "The goal is to connect five of your pieces in a row horizontally, vertically, or diagonally.\n\n"
        f"Current board state (Turn {turn_number}):\n{board_str}\n\n"
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
                return None
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
                    return None
                move = int(move_match.group(1)) - 1  # Convert to 0-indexed
        
        if move not in range(COLUMN_COUNT) or not is_valid_location(board, move):
            print(f"❌ Claude suggested an invalid move: {move+1}. Valid moves are: {valid_columns}")
            return None
            
        return move
    except Exception as e:
        print(f"❌ Error getting move from Claude: {str(e)}")
        return None

def play_gpt_vs_claude():
    board = create_board()
    game_over = False
    turn = 0
    
    # Reset game history at the start of a new game
    global game_history
    game_history = []
    
    print("\n🎮 Welcome to Connect 5: GPT-4 vs Claude!")
    print("Player 1: X (GPT-4)")
    print("Player 2: O (Claude)")
    print("\nInitial board state:")
    print(board_to_string(board))
    draw_board(board)

    while not game_over:
        # Rate limiting: 1 second pause between moves
        time.sleep(1)
        
        current_player = 1 if turn % 2 == 0 else 2
        ai_name = "GPT-4" if current_player == 1 else "Claude"
        print(f"\n🎯 Player {current_player} ({ai_name})'s turn... (Turn {turn+1})")
        
        if current_player == 1:
            col = get_move_from_gpt(board, current_player, turn+1)
        else:
            col = get_move_from_claude(board, current_player, turn+1)
        
        # Validate move
        if col is None or not is_valid_location(board, col):
            print(f"❌ Invalid move from {ai_name}. Retrying...")
            continue
        
        row = get_next_open_row(board, col)
        drop_piece(board, row, col, current_player)
        
        # Record the move in game history
        game_history.append({
            "turn": turn + 1,
            "player": current_player,
            "column": col + 1  # Store 1-indexed for display
        })
        
        print(f"✅ {ai_name} drops piece in column {col+1}")
        print("\nCurrent board state:")
        print(board_to_string(board))
        draw_board(board)
        
        if winning_move(board, current_player):
            print(f"\n🎉 {ai_name} (Player {current_player}) wins! 🎉")
            game_over = True
        elif all(board[ROW_COUNT-1][c] != 0 for c in range(COLUMN_COUNT)):
            print("\n🤝 The game is a draw!")
            game_over = True
        
        turn += 1
        # We'll add a second delay after each full turn as well for better visualization
        time.sleep(1)

if __name__ == '__main__':
    play_gpt_vs_claude()