import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, Rectangle

def draw_board(board):
    """
    Visualizes the Connect board using matplotlib.
    
    Parameters:
        board (np.array): A NumPy array representing the board state.
    """
    ROW_COUNT, COLUMN_COUNT = board.shape

    # Close any existing figures to prevent multiple windows
    plt.close('all')
    
    # Create a new figure
    fig, ax = plt.subplots(figsize=(COLUMN_COUNT, ROW_COUNT))

    board_width = COLUMN_COUNT
    board_height = ROW_COUNT
    board_background = Rectangle((0, 0), board_width, board_height, color='blue')
    ax.add_patch(board_background)
    
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            x = c + 0.5
            y = r + 0.5
            circle = Circle((x, y), 0.4, facecolor='white', edgecolor='black')
            ax.add_patch(circle)
    
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            piece = board[r][c]
            if piece == 1 or piece == 2:
                x = c + 0.5
                y = r + 0.5
                color = 'red' if piece == 1 else 'yellow'
                piece_circle = Circle((x, y), 0.4, facecolor=color, edgecolor='black')
                ax.add_patch(piece_circle)

    ax.set_xlim(0, COLUMN_COUNT)
    ax.set_ylim(0, ROW_COUNT)
    ax.set_aspect('equal')
    ax.axis('off')
    
    plt.draw()  
    plt.pause(0.1)