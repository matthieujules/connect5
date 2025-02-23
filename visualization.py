import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, Rectangle


def draw_board(board):
    """
    Visualizes the Connect 4 board using matplotlib.
    
    Parameters:
        board (np.array): A 6x7 NumPy array representing the board state.
    """
    ROW_COUNT, COLUMN_COUNT = board.shape

    plt.clf() 
    fig, ax = plt.subplots()

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

if __name__ == '__main__':
    board = np.zeros((6, 7), dtype=int)
    board[5][0] = 1  
    board[5][1] = 2  
    board[4][0] = 1  
    board[5][2] = 1  
    board[4][1] = 2  
    board[3][0] = 1  
    
    draw_board(board)
