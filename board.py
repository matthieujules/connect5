"""
Connect 5 with Rotation - Board Module
Contains all the board related functions and classes
"""
import numpy as np

# Game board dimensions
ROW_COUNT = 8
COLUMN_COUNT = 9

# Rotation interval - board rotates every N moves (representing turns for both players)
ROTATION_INTERVAL = 6

def create_board():
    """Create a new empty game board."""
    return np.zeros((ROW_COUNT, COLUMN_COUNT), dtype=int)

def drop_piece(board, row, col, piece):
    """Place a piece at the specified position."""
    board[row][col] = piece

def is_valid_location(board, col, rotation_state=0):
    """
    Check if a column has space for another piece.
    Gravity always pulls downward regardless of rotation state.
    """
    # Get current dimensions
    ROWS, COLS = board.shape
    
    # Check if column is in valid range and if the top cell is empty
    return 0 <= col < COLS and board[ROWS - 1, col] == 0

def get_next_open_row(board, col, rotation_state=0):
    """
    Find the next open row in a column.
    Gravity always pulls downward regardless of rotation state.
    """
    # Get current dimensions
    ROWS, COLS = board.shape
    
    # Ensure column is in valid range
    if not 0 <= col < COLS:
        return None
    
    # Always search from bottom up (gravity pulls down)
    for r in range(ROWS):
        if board[r, col] == 0:
            return r
    
    return None

def get_valid_moves(board, rotation_state=0):
    """
    Get a list of all valid moves in the current board state.
    """
    # Get current dimensions
    ROWS, COLS = board.shape
    
    # Valid moves are columns that aren't full
    return [col for col in range(COLS) if is_valid_location(board, col, rotation_state)]

def rotate_board_clockwise(board):
    """
    Rotate the board 90 degrees clockwise.
    For non-square boards, this requires special handling.
    """
    # For non-square matrices, we need to handle rotation carefully
    rows, cols = board.shape
    # Create a new array with swapped dimensions
    rotated = np.zeros((cols, rows), dtype=int)
    
    # Manually perform the rotation to ensure correctness
    for r in range(rows):
        for c in range(cols):
            # In a 90-degree clockwise rotation:
            # new_col = rows - 1 - old_row
            # new_row = old_col
            rotated[c][rows - 1 - r] = board[r][c]
    
    return rotated

def apply_gravity_after_rotation(board, rotation_state=0):
    """
    Apply gravity to all pieces after rotation.
    Gravity always pulls downward (to the bottom of the board).
    """
    # Get current dimensions after rotation
    CURRENT_ROWS, CURRENT_COLS = board.shape
    new_board = np.zeros_like(board)
    
    # Apply gravity column by column (downward)
    for col in range(CURRENT_COLS):
        # Get all non-zero pieces in this column
        pieces = []
        for row in range(CURRENT_ROWS):
            if board[row, col] != 0:
                pieces.append(board[row, col])
        
        # Place pieces at the bottom of the column
        for i, piece in enumerate(pieces):
            if i < CURRENT_ROWS:  # Safety check
                new_board[i, col] = piece
    
    return new_board

def winning_move(board, piece):
    """Check if the given piece has a winning configuration."""
    # Get current dimensions of the board
    rows, cols = board.shape
    
    # Check if board is big enough for a win (need at least 5 in either dimension)
    if rows < 5 and cols < 5:
        return False
    
    try:
        # Horizontal
        for r in range(rows):
            for c in range(cols - 4):
                if all(board[r, c + i] == piece for i in range(5)):
                    return True

        # Vertical
        for c in range(cols):
            for r in range(rows - 4):
                if all(board[r + i, c] == piece for i in range(5)):
                    return True

        # Diagonal (positive slope)
        for c in range(cols - 4):
            for r in range(rows - 4):
                if all(board[r + i, c + i] == piece for i in range(5)):
                    return True

        # Diagonal (negative slope)
        for c in range(cols - 4):
            for r in range(4, rows):
                if all(board[r - i, c + i] == piece for i in range(5)):
                    return True
    except IndexError:
        # If we get an index error, return False (no win)
        return False

    return False

def board_to_string(board, rotation_state=0):
    """
    Convert the board to a string representation that's intuitive regardless of rotation.
    Always shows the board with gravity pulling down, with pieces shown as they appear visually.
    """
    symbols = {0: '.', 1: 'X', 2: 'O'}
    rows = []
    
    # Get current dimensions of the board
    current_rows, current_cols = board.shape
    
    # Direction labels
    rotation_labels = [
        "Original orientation",
        "Rotated 90° clockwise",
        "Rotated 180°",
        "Rotated 270° clockwise"
    ]
    direction = f"{rotation_labels[rotation_state % 4]} (gravity pulls down)"
    rows.append(direction)
    
    # Always display the board in a natural top-down view (like the visual representation)
    try:
        # Show the board top-to-bottom
        for r in range(current_rows-1, -1, -1):  # Flip board vertically for display
            row_chars = []
            for c in range(current_cols):
                row_chars.append(symbols[board[r, c]])
            rows.append(' '.join(row_chars))
            
        # Add column numbers at the bottom
        valid_moves = ' '.join(str(i) for i in range(1, current_cols + 1))
        rows.append(valid_moves)
    except IndexError as e:
        # Provide helpful error info if there's still an index issue
        rows.append(f"Error rendering board: {str(e)}")
        rows.append(f"Board shape: {board.shape}, Rotation: {rotation_state % 4}")
    
    return '\n'.join(rows)

def is_board_full(board, rotation_state=0):
    """Check if the board is full."""
    # Get current dimensions of the board
    current_rows, current_cols = board.shape
    
    # Board is full if the top row is completely filled
    return all(board[current_rows-1, c] != 0 for c in range(current_cols))