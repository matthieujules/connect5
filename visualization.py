"""
Connect 5 with Rotation - Visualization Module
Contains functions for visualizing the game board
"""
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, Rectangle, Arrow

def draw_board(board, rotation_state=0):
    """
    Visualizes the Connect board using matplotlib with rotation support.
    
    Parameters:
        board (np.array): A NumPy array representing the board state.
        rotation_state (int): The current rotation state of the board (0-3).
    """
    # Get current dimensions of the board (may have changed after rotation)
    current_rows, current_cols = board.shape

    # Close any existing figures to prevent multiple windows
    plt.close('all')
    
    # Create a new figure
    fig, ax = plt.subplots(figsize=(max(current_cols, current_rows), max(current_cols, current_rows)))

    # Draw background
    board_width = current_cols
    board_height = current_rows
    board_background = Rectangle((0, 0), board_width, board_height, color='blue')
    ax.add_patch(board_background)
    
    # Draw empty spaces and pieces
    try:
        # Draw empty spaces
        for c in range(current_cols):
            for r in range(current_rows):
                x = c + 0.5
                y = r + 0.5
                circle = Circle((x, y), 0.4, facecolor='white', edgecolor='black')
                ax.add_patch(circle)
        
        # Draw pieces
        for c in range(current_cols):
            for r in range(current_rows):
                piece = board[r, c]
                if piece == 1 or piece == 2:
                    x = c + 0.5
                    y = r + 0.5
                    color = 'red' if piece == 1 else 'yellow'
                    piece_circle = Circle((x, y), 0.4, facecolor=color, edgecolor='black')
                    ax.add_patch(piece_circle)
    except IndexError as e:
        # If there's an index error, add text explaining the issue
        plt.figtext(0.5, 0.5, f"Error drawing board: {str(e)}\nBoard shape: {board.shape}", 
                    ha="center", fontsize=12, color='red')

    # Always show gravity arrow pointing down
    gravity_direction = "↓"
    
    # Position gravity indicator at the top of the board pointing down
    arrow_x = board_width / 2
    arrow_y = board_height + 0.5
    arrow_dx = 0
    arrow_dy = -1
    
    # Add text to indicate gravity and rotation state
    plt.figtext(0.5, 0.01, f"Rotation State: {rotation_state % 4} | Gravity: {gravity_direction} | Board: {current_rows}x{current_cols}", 
                ha="center", fontsize=12)
    
    # Add an arrow to show gravity direction
    arrow = Arrow(arrow_x, arrow_y, arrow_dx, arrow_dy, width=0.5, color='black')
    ax.add_patch(arrow)
    
    # Set plot limits with extra space for arrows
    ax.set_xlim(-1, current_cols + 1)
    ax.set_ylim(-1, current_rows + 1)
    ax.set_aspect('equal')
    ax.axis('off')
    
    plt.draw()  
    plt.pause(0.1)