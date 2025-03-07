"""
Connect 5 with Rotation - Main Game Module
Contains the main game loop for the GPT vs Claude match
"""
import random
import time

from ai_players import get_move_from_gpt, get_move_from_claude, get_random_valid_move, game_history
from board import (
    create_board, drop_piece, get_next_open_row, is_valid_location, 
    winning_move, board_to_string, rotate_board_clockwise, 
    apply_gravity_after_rotation, is_board_full, ROTATION_INTERVAL
)
from visualization import draw_board

def play_gpt_vs_claude():
    """
    Main game loop for GPT vs Claude Connect 5 with rotation.
    """
    # Initialize game state
    board = create_board()
    game_over = False
    turn = 0
    rotation_state = 0
    
    # Reset game history at the start of a new game
    global game_history
    game_history.clear()
    
    # Welcome message
    print("\n🎮 Welcome to Connect 5 with Rotation: GPT-4 vs Claude!")
    print("Player 1: X (GPT-4)")
    print("Player 2: O (Claude)")
    print(f"Board will rotate 90° clockwise every {ROTATION_INTERVAL} moves (3 turns each player)")
    print("After rotation, gravity always pulls pieces downward")
    print("\nInitial board state:")
    print(board_to_string(board, rotation_state))
    draw_board(board, rotation_state)

    # Main game loop
    while not game_over:
        # Rate limiting: 1 second pause between moves
        time.sleep(1)
        
        # Determine current player
        current_player = 1 if turn % 2 == 0 else 2
        ai_name = "GPT-4" if current_player == 1 else "Claude"
        print(f"\n🎯 Player {current_player} ({ai_name})'s turn... (Turn {turn+1}, Rotation: {rotation_state % 4})")
        
        # Check if we're approaching a rotation point
        moves_until_rotation = ROTATION_INTERVAL - ((turn + 1) % ROTATION_INTERVAL)
        if moves_until_rotation == 1:
            print("⚠️ Board will rotate after 1 more move!")
        elif moves_until_rotation <= 3:
            print(f"ℹ️ Board will rotate after {moves_until_rotation} more moves.")
        
        # Get a move from the AI (will fall back to random valid move if AI fails)
        if current_player == 1:
            col = get_move_from_gpt(board, current_player, turn+1, rotation_state)
        else:
            col = get_move_from_claude(board, current_player, turn+1, rotation_state)
        
        # If we somehow got an invalid move (shouldn't happen with fallback to random), try again
        if col is None or not is_valid_location(board, col, rotation_state):
            print(f"❌ Invalid move from {ai_name}. Using random valid move...")
            col = get_random_valid_move(board, rotation_state)
            if col is None:  # If still no valid moves, the board might be full
                print("No valid moves available. Game is a draw.")
                game_over = True
                continue
        
        # Find the row based on current gravity direction
        row = get_next_open_row(board, col, rotation_state)
        drop_piece(board, row, col, current_player)
        
        # Record the move in game history
        game_history.append({
            "turn": turn + 1,
            "player": current_player,
            "column": col + 1,  # Store 1-indexed for display
            "rotation": rotation_state % 4
        })
        
        print(f"✅ {ai_name} drops piece at position {col+1}")
        print("\nCurrent board state:")
        print(board_to_string(board, rotation_state))
        draw_board(board, rotation_state)
        
        # Check if the game is over
        if winning_move(board, current_player):
            print(f"\n🎉 {ai_name} (Player {current_player}) wins! 🎉")
            game_over = True
        # Check for a draw
        elif is_board_full(board, rotation_state):
            print("\n🤝 The game is a draw!")
            game_over = True
        
        turn += 1
        
        # Rotate the board every ROTATION_INTERVAL moves
        if turn % ROTATION_INTERVAL == 0 and not game_over:
            print("\n🔄 Rotating board 90 degrees clockwise...")
            print("All pieces will fall downward due to gravity after rotation.")
            try:
                # Store the current dimensions
                current_rows, current_cols = board.shape
                
                # First, rotate the board
                rotated_board = rotate_board_clockwise(board)
                
                # Make sure we're working with the expected dimensions after rotation
                if rotated_board.shape != (current_cols, current_rows):
                    print(f"❌ Warning: Expected dimensions after rotation to be {(current_cols, current_rows)}, got {rotated_board.shape}")
                    print("Creating a correctly shaped board...")
                    # Create a correctly shaped board manually
                    correct_board = np.zeros((current_cols, current_rows), dtype=int)
                    for r in range(min(current_rows, rotated_board.shape[0])):
                        for c in range(min(current_cols, rotated_board.shape[1])):
                            try:
                                correct_board[c, r] = rotated_board[c, r]
                            except IndexError:
                                pass
                    rotated_board = correct_board
                
                # Then apply gravity to make pieces fall according to new direction
                board = apply_gravity_after_rotation(rotated_board, rotation_state + 1)
                
                # Update rotation state
                rotation_state += 1
                
                # Show the board after rotation
                print("\nBoard after rotation:")
                print(board_to_string(board, rotation_state))
                draw_board(board, rotation_state)
            except Exception as e:
                print(f"❌ Error during rotation: {str(e)}")
                print("Continuing without rotation...")
            
        # Add a short delay after each full turn for better visualization
        time.sleep(1)

if __name__ == '__main__':
    play_gpt_vs_claude()