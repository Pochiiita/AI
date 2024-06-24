import tkinter as tk
import numpy as np
import random
import csv

# Define the Scrabble board size
BOARD_SIZE = 15

# Create the board with special tiles (DL, TL, DW, TW)
board = np.full((BOARD_SIZE, BOARD_SIZE), "", dtype='<U2')
special_tiles = np.array([
    ['TW', '', '', 'DL', '', '', '', 'TW', '', '', '', 'DL', '', '', 'TW'],
    ['', 'DW', '', '', '', 'TL', '', '', '', 'TL', '', '', '', 'DW', ''],
    ['', '', 'DW', '', '', '', 'DL', '', 'DL', '', '', '', 'DW', '', ''],
    ['DL', '', '', 'DW', '', '', '', 'DL', '', '', '', 'DW', '', '', 'DL'],
    ['', '', '', '', 'DW', '', '', '', '', '', 'DW', '', '', '', ''],
    ['', 'TL', '', '', '', 'TL', '', '', '', 'TL', '', '', '', 'TL', ''],
    ['', '', 'DL', '', '', '', 'DL', '', 'DL', '', '', '', 'DL', '', ''],
    ['TW', '', '', 'DL', '', '', '', 'DW', '', '', '', 'DL', '', '', 'TW'],
    ['', '', 'DL', '', '', '', 'DL', '', 'DL', '', '', '', 'DL', '', ''],
    ['', 'TL', '', '', '', 'TL', '', '', '', 'TL', '', '', '', 'TL', ''],
    ['', '', '', '', 'DW', '', '', '', '', '', 'DW', '', '', '', ''],
    ['DL', '', '', 'DW', '', '', '', 'DL', '', '', '', 'DW', '', '', 'DL'],
    ['', '', 'DW', '', '', '', 'DL', '', 'DL', '', '', '', 'DW', '', ''],
    ['', 'DW', '', '', '', 'TL', '', '', '', 'TL', '', '', '', 'DW', ''],
    ['TW', '', '', 'DL', '', '', '', 'TW', '', '', '', 'DL', '', '', 'TW']
], dtype='<U2')

# Define the Scrabble tiles and points (simplified)
TILES = {
    'A': 1, 'B': 3, 'K': 5, 'D': 2, 'E': 1, 'G': 2, 'H': 4, 'I': 1,
    'L': 1, 'M': 3, 'N': 1, 'NG': 4, 'O': 1, 'P': 3, 'R': 1, 'S': 1,
    'T': 1, 'U': 1, 'W': 4, 'Y': 4, 'Z': 4, 'C': 3, '': 0
}

# Create a pool of tiles for random selection
tile_pool = [tile for tile, count in TILES.items() for _ in range(12 if tile == '' else 1)]
random.shuffle(tile_pool)

# Load the word list from a CSV file
def load_word_list(filename):
    with open(filename, 'r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        return set(row[0].strip().upper() for row in reader)

# Load the Tagalog words
WORD_LIST_FILE = 'tagalog_dict.csv'
WORD_SET = load_word_list(WORD_LIST_FILE)

# Game state variables
player_tiles = [random.sample(tile_pool, 7), random.sample(tile_pool, 7)]
turn = 0  # 0 for player, 1 for AI

# Heuristic evaluation function
def evaluate_board(board):
    """Evaluate the board by summing the points of all tiles on the board."""
    score = 0
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            tile = board[i, j]
            if tile in TILES:
                multiplier = 1
                if special_tiles[i, j] == 'DL':
                    multiplier = 2
                elif special_tiles[i, j] == 'TL':
                    multiplier = 3
                score += TILES[tile] * multiplier
    return score

def is_valid_move(board, word, start_pos, direction):
    """Check if placing the word on the board is valid."""
    x, y = start_pos
    if direction == 'H':
        if y + len(word) > BOARD_SIZE:
            return False
        for i in range(len(word)):
            if board[x, y + i] not in ("", word[i]):
                return False
    elif direction == 'V':
        if x + len(word) > BOARD_SIZE:
            return False
        for i in range(len(word)):
            if board[x + i, y] not in ("", word[i]):
                return False
    return True

def place_word(board, word, start_pos, direction):
    """Place a word on the board."""
    x, y = start_pos
    for i in range(len(word)):
        if direction == 'H':
            board[x, y + i] = word[i]
        elif direction == 'V':
            board[x + i, y] = word[i]

def remove_word(board, word, start_pos, direction):
    """Remove a word from the board (for backtracking)."""
    x, y = start_pos
    for i in range(len(word)):
        if direction == 'H':
            board[x, y + i] = ""
        elif direction == 'V':
            board[x + i, y] = ""

def alpha_beta(board, depth, alpha, beta, maximizing_player, tiles):
    """Alpha-beta pruning algorithm with heuristic evaluation."""
    if depth == 0 or not tiles:
        return evaluate_board(board)

    if maximizing_player:
        max_eval = float('-inf')
        for word in WORD_SET:
            if all(tile in tiles for tile in word):
                for x in range(BOARD_SIZE):
                    for y in range(BOARD_SIZE):
                        for direction in ['H', 'V']:
                            if is_valid_move(board, word, (x, y), direction):
                                place_word(board, word, (x, y), direction)
                                eval = alpha_beta(board, depth - 1, alpha, beta, False, tiles)
                                remove_word(board, word, (x, y), direction)
                                max_eval = max(max_eval, eval)
                                alpha = max(alpha, eval)
                                if beta <= alpha:
                                    break
        return max_eval
    else:
        min_eval = float('inf')
        for word in WORD_SET:
            if all(tile in tiles for tile in word):
                for x in range(BOARD_SIZE):
                    for y in range(BOARD_SIZE):
                        for direction in ['H', 'V']:
                            if is_valid_move(board, word, (x, y), direction):
                                place_word(board, word, (x, y), direction)
                                eval = alpha_beta(board, depth - 1, alpha, beta, True, tiles)
                                remove_word(board, word, (x, y), direction)
                                min_eval = min(min_eval, eval)
                                beta = min(beta, eval)
                                if beta <= alpha:
                                    break
        return min_eval

def find_best_move(board, depth=3):
    """Find the best move for the AI using alpha-beta pruning."""
    best_score = float('-inf')
    best_move = None
    for word in WORD_SET:
        if all(tile in player_tiles[1] for tile in word):
            for x in range(BOARD_SIZE):
                for y in range(BOARD_SIZE):
                    for direction in ['H', 'V']:
                        if is_valid_move(board, word, (x, y), direction):
                            place_word(board, word, (x, y), direction)
                            move_score = alpha_beta(board, depth - 1, float('-inf'), float('inf'), False, player_tiles[1])
                            remove_word(board, word, (x, y), direction)
                            if move_score > best_score:
                                best_score = move_score
                                best_move = (word, (x, y), direction)
    return best_move

# GUI functions
def update_board_gui():
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            tile = board[i, j] if board[i, j] else special_tiles[i, j] if special_tiles[i, j] else '.'
            board_buttons[i][j].config(text=tile)

def update_tiles_gui():
    for idx, button in enumerate(tile_buttons):
        button.config(text=player_tiles[0][idx] if idx < len(player_tiles[0]) else '')

def start_drag(event):
    widget = event.widget
    widget.startX = event.x
    widget.startY = event.y

def drag_motion(event):
    widget = event.widget
    x = widget.winfo_x() - widget.startX + event.x
    y = widget.winfo_y() - widget.startY + event.y
    widget.place(x=x, y=y)

def drop_tile(event):
    widget = event.widget
    x, y = event.x_root - board_frame.winfo_rootx(), event.y_root - board_frame.winfo_rooty()
    board_x, board_y = x // 40, y // 40

    if 0 <= board_x < BOARD_SIZE and 0 <= board_y < BOARD_SIZE:
        tile = widget.cget("text")
        if is_valid_move(board, tile, (board_x, board_y), 'H'):
            place_word(board, tile, (board_x, board_y), 'H')
            player_tiles[0].remove(tile)
            update_board_gui()
            update_tiles_gui()
            if not player_tiles[0]:
                ai_move()

def ai_move():
    status_label.config(text="AI is thinking...")
    best_move = find_best_move(board)
    if best_move:
        word, pos, direction = best_move
        place_word(board, word, pos, direction)
        update_board_gui()
        status_label.config(text=f"AI placed {word} at {pos} going {direction}")
    else:
        status_label.config(text="AI cannot make a move. Game over!")
    replenish_tiles()

def replenish_tiles():
    for i in range(7 - len(player_tiles[0])):
        if tile_pool:
            player_tiles[0].append(tile_pool.pop())
    for i in range(7 - len(player_tiles[1])):
        if tile_pool:
            player_tiles[1].append(tile_pool.pop())
    update_tiles_gui()

# Create the main window
root = tk.Tk()
root.title("Tagalog Scrabble Game")

# Create the board grid
board_frame = tk.Frame(root)
board_frame.pack()

board_buttons = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
for i in range(BOARD_SIZE):
    for j in range(BOARD_SIZE):
        board_buttons[i][j] = tk.Button(board_frame, text='.', width=4, height=2)
        board_buttons[i][j].grid(row=i, column=j)

# Create the player's tile rack
tile_frame = tk.Frame(root)
tile_frame.pack()

tile_buttons = []
for i in range(7):
    tile_button = tk.Button(tile_frame, text='', width=4, height=2)
    tile_button.grid(row=0, column=i)
    tile_button.bind("<Button-1>", start_drag)
    tile_button.bind("<B1-Motion>", drag_motion)
    tile_button.bind("<ButtonRelease-1>", drop_tile)
    tile_buttons.append(tile_button)

status_label = tk.Label(root, text="Your turn!")
status_label.pack()

# Initial GUI update
update_board_gui()
update_tiles_gui()

# Start the Tkinter main loop
root.mainloop()
