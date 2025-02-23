import numpy as np

from visualization import draw_board

ROW_COUNT = 8
COLUMN_COUNT = 9

def create_board():
    board = np.zeros((ROW_COUNT, COLUMN_COUNT), dtype=int)
    return board

def drop_piece(board, row, col, piece):
    board[row][col] = piece

def is_valid_location(board, col):
    return board[ROW_COUNT - 1][col] == 0

def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r

def winning_move(board, piece):
    for c in range(COLUMN_COUNT - 4):
        for r in range(ROW_COUNT):
            if (board[r][c] == piece and 
                board[r][c+1] == piece and 
                board[r][c+2] == piece and 
                board[r][c+3] == piece and 
                board[r][c+4] == piece):
                return True

    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT - 4):
            if (board[r][c] == piece and 
                board[r+1][c] == piece and 
                board[r+2][c] == piece and 
                board[r+3][c] == piece and
                board[r+4][c] == piece):
                return True

    for c in range(COLUMN_COUNT - 4):
        for r in range(ROW_COUNT - 4):
            if (board[r][c] == piece and 
                board[r+1][c+1] == piece and 
                board[r+2][c+2] == piece and 
                board[r+3][c+3] == piece and
                board[r+4][c+4] == piece):
                return True

    for c in range(COLUMN_COUNT - 4):
        for r in range(4, ROW_COUNT):
            if (board[r][c] == piece and 
                board[r-1][c+1] == piece and 
                board[r-2][c+2] == piece and 
                board[r-3][c+3] == piece and
                board[r-4][c+4] == piece):
                return True
    return False

def print_board(board):
    print(np.flip(board, 0))

def play_game():
    board = create_board()
    game_over = False
    turn = 0

    print("\nWelcome to Connect 5!")
    print("Player 1: Red (shown as 1)")
    print("Player 2: Yellow (shown as 2)")
    print("Get 5 in a row to win!")
    print("\nCurrent board state:")
    print_board(board)
    draw_board(board)

    while not game_over:
        if turn == 0:
            print("\nPlayer 1's turn (Red)")
            col = int(input(f"Select a column (0-{COLUMN_COUNT-1}): "))
            piece = 1
        else:
            print("\nPlayer 2's turn (Yellow)")
            col = int(input(f"Select a column (0-{COLUMN_COUNT-1}): "))
            piece = 2

        if 0 <= col < COLUMN_COUNT and is_valid_location(board, col):
            row = get_next_open_row(board, col)
            drop_piece(board, row, col, piece)

            if winning_move(board, piece):
                print("\nCurrent board state:")
                print_board(board)
                draw_board(board)
                print(f"\n🎉 Player {piece} wins! 🎉")
                game_over = True
            else:
                print("\nCurrent board state:")
                print_board(board)
                draw_board(board)
                if all(board[ROW_COUNT-1][c] != 0 for c in range(COLUMN_COUNT)):
                    print("\nThe game is a draw! 🤝")
                    game_over = True

            turn = (turn + 1) % 2
        else:
            print("\n❌ Invalid move. Please try again.")

if __name__ == '__main__':
    play_game()
