import csv
from random import shuffle

# Keeps track of the score-worth of each letter-tile.
LETTER_VALUES = {"A": 1, "B": 3, "C": 3, "D": 2, "E": 1, "F": 4, "G": 2, "H": 4, "I": 1, "J": 8, "K": 5,
                 "L": 1, "M": 3, "N": 1, "O": 1, "P": 3, "Q": 10, "R": 1, "S": 1, "T": 1, "U": 1, "V": 4,
                 "W": 4, "X": 8, "Y": 4, "Z": 10, "#": 0, "NG": 5, "NANG": 5, "Ñ": 6}

# Global variable to store valid words
valid_words = set()

def load_tagalog_dictionary(file_path):
    global valid_words
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            valid_words.add(row[0].strip().upper())

load_tagalog_dictionary('tagalog_dict.csv')

class Tile:
    def __init__(self, letter, letter_values):
        self.letter = letter.upper()
        self.score = letter_values.get(self.letter, 0)

    def get_letter(self):
        return self.letter

    def get_score(self):
        return self.score

class Bag:
    def __init__(self):
        self.bag = []
        self.initialize_bag()

    def add_to_bag(self, tile, quantity):
        for _ in range(quantity):
            self.bag.append(tile)

    def initialize_bag(self):
        global LETTER_VALUES
        tile_quantities = {
            "A": 9, "B": 2, "C": 2, "D": 4, "E": 12, "F": 2, "G": 3, "H": 2, "I": 9, "J": 1, "K": 1,
            "L": 4, "M": 2, "N": 6, "O": 8, "P": 2, "Q": 1, "R": 6, "S": 4, "T": 6, "U": 4, "V": 2,
            "W": 2, "X": 1, "Y": 2, "Z": 1, "#": 2, "NG": 2, "NANG": 2, "Ñ": 3
        }
        for letter, quantity in tile_quantities.items():
            self.add_to_bag(Tile(letter, LETTER_VALUES), quantity)
        shuffle(self.bag)

    def take_from_bag(self):
        return self.bag.pop()

    def get_remaining_tiles(self):
        return len(self.bag)

class Rack:
    def __init__(self, bag):
        self.rack = []
        self.bag = bag
        self.initialize()

    def add_to_rack(self):
        self.rack.append(self.bag.take_from_bag())

    def initialize(self):
        for _ in range(7):
            self.add_to_rack()

    def get_rack_str(self):
        return ", ".join(tile.get_letter() for tile in self.rack)

    def get_rack_arr(self):
        return self.rack

    def remove_from_rack(self, tile):
        self.rack.remove(tile)

    def get_rack_length(self):
        return len(self.rack)

    def replenish_rack(self):
        while self.get_rack_length() < 7 and self.bag.get_remaining_tiles() > 0:
            self.add_to_rack()

class Player:
    def __init__(self, bag, is_human=True):
        self.name = ""
        self.rack = Rack(bag)
        self.score = 0
        self.is_human = is_human

    def set_name(self, name):
        self.name = name

    def get_name(self):
        return self.name

    def get_rack_str(self):
        return self.rack.get_rack_str()

    def get_rack_arr(self):
        return self.rack.get_rack_arr()

    def increase_score(self, increase):
        self.score += increase

    def get_score(self):
        return self.score

    def is_human_player(self):
        return self.is_human

    def get_rack_length(self):
        return self.rack.get_rack_length()

class AIPlayer(Player):
    def __init__(self, bag):
        super().__init__(bag, is_human=False)

    def generate_move(self, board, players):
        best_move = None
        best_score = float('-inf')
        depth = 5
        for move in self.get_all_possible_moves(board):
            if self.is_valid_move(move, board):
                board.place_word(move[0], move[1], move[2], self)
                score = self.alpha_beta_pruning(board, depth, float('-inf'), float('inf'), True, players)
                board.remove_word(move[0], move[1], move[2])
                if score > best_score:
                    best_score = score
                    best_move = move
        return best_move

    def get_all_possible_moves(self, board):
        moves = []
        for tile in self.rack.get_rack_arr():
            for row in range(15):
                for col in range(15):
                    if board.board[row][col] == ' ':
                        if col + 1 <= 15:
                            moves.append((tile.get_letter(), (row, col), 'right'))
                        if row + 1 <= 15:
                            moves.append((tile.get_letter(), (row, col), 'down'))
        return moves

    def is_valid_move(self, move, board):
        letter, (row, col), direction = move
        if direction == 'right':
            if col + 1 > 15:
                return False
        elif direction == 'down':
            if row + 1 > 15:
                return False
        return True

    def alpha_beta_pruning(self, board, depth, alpha, beta, maximizing_player, players):
        if depth == 0:
            return self.heuristic_evaluation(board, players)
        if maximizing_player:
            max_eval = float('-inf')
            for move in self.get_all_possible_moves(board):
                if self.is_valid_move(move, board):
                    board.place_word(move[0], move[1], move[2], self)
                    eval = self.alpha_beta_pruning(board, depth-1, alpha, beta, False, players)
                    board.remove_word(move[0], move[1], move[2])
                    max_eval = max(max_eval, eval)
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break
            return max_eval
        else:
            min_eval = float('inf')
            for move in self.get_all_possible_moves(board):
                if self.is_valid_move(move, board):
                    board.place_word(move[0], move[1], move[2], self)
                    eval = self.alpha_beta_pruning(board, depth-1, alpha, beta, True, players)
                    board.remove_word(move[0], move[1], move[2])
                    min_eval = min(min_eval, eval)
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break
            return min_eval

    def heuristic_evaluation(self, board, players):
        ai_score = self.get_score()
        human_score = next(player.get_score() for player in players if player.is_human_player())
        return ai_score - human_score

class Board:
    def __init__(self):
        self.board = [[' ' for _ in range(15)] for _ in range(15)]
        self.add_premium_squares()

    def get_board(self, players):
        board_str = "   |  " + "  |  ".join(str(item) for item in range(10)) + "  | " + "  | ".join(str(item) for item in range(10, 15)) + " |\n"
        board_str += "   " + "_ " * 29 + "_\n"
        for i, row in enumerate(self.board):
            row_str = str(i).rjust(2) + " | " + " | ".join(row) + " |"
            board_str += row_str + "\n"
            board_str += "   " + "|_" * 29 + "|\n"

        score_str = "\nScores:\n"
        for player in players:
            score_str += player.get_name() + ": " + str(player.get_score()) + "\n"

        return board_str + score_str

    def add_premium_squares(self):
        TRIPLE_WORD_SCORE = ((0,0), (7, 0), (14,0), (0, 7), (14, 7), (0, 14), (7, 14), (14, 14))
        DOUBLE_WORD_SCORE = ((1, 1), (2, 2), (3, 3), (4, 4), (7, 7), (10, 10), (11, 11), (12, 12), (13, 13))
        TRIPLE_LETTER_SCORE = ((1, 5), (5, 1), (9, 1), (13, 5), (5, 13), (9, 13), (1, 9), (13, 9))
        DOUBLE_LETTER_SCORE = ((0, 3), (0, 11), (2, 6), (2, 8), (3, 0), (3, 7), (3, 14), (6, 2), (6, 6), (6, 8), (6, 12), (7, 3), (7, 11), (8, 2), (8, 6), (8, 8), (8, 12), (11, 0), (11, 7), (11, 14), (12, 6), (12, 8), (14, 3), (14, 11))

        for x, y in TRIPLE_WORD_SCORE:
            self.board[x][y] = "TW"
        for x, y in DOUBLE_WORD_SCORE:
            self.board[x][y] = "DW"
        for x, y in TRIPLE_LETTER_SCORE:
            self.board[x][y] = "TL"
        for x, y in DOUBLE_LETTER_SCORE:
            self.board[x][y] = "DL"

    def place_word(self, word, position, direction, player):
        row, col = position
        if direction == 'right':
            for i, letter in enumerate(word):
                self.board[row][col + i] = letter
        elif direction == 'down':
            for i, letter in enumerate(word):
                self.board[row + i][col] = letter

    def remove_word(self, word, position, direction):
        row, col = position
        if direction == 'right':
            for i, letter in enumerate(word):
                self.board[row][col + i] = ' '
        elif direction == 'down':
            for i, letter in enumerate(word):
                self.board[row + i][col] = ' '

class Game:
    def __init__(self):
        self.bag = Bag()
        self.players = []
        self.current_player_index = 0
        self.board = Board()

    def add_player(self, player):
        self.players.append(player)

    def start_game(self):
        while not self.is_game_over():
            self.play_turn()

    def play_turn(self):
        current_player = self.players[self.current_player_index]
        print(self.board.get_board(self.players))
        print(f"{current_player.get_name()}'s turn. Current rack: {current_player.get_rack_str()}")
        if current_player.is_human_player():
            word, position, direction = self.get_human_move()
        else:
            move = current_player.generate_move(self.board, self.players)
            word, position, direction = move

        self.board.place_word(word, position, direction, current_player)
        current_player.increase_score(self.calculate_word_score(word, position, direction))
        current_player.rack.replenish_rack()
        self.current_player_index = (self.current_player_index + 1) % len(self.players)

    def get_human_move(self):
        word = input("Enter the word to place: ").upper()
        row = int(input("Enter the starting row: "))
        col = int(input("Enter the starting column: "))
        direction = input("Enter the direction (right or down): ").lower()
        return word, (row, col), direction

    def calculate_word_score(self, word, position, direction):
        row, col = position
        score = 0
        if direction == 'right':
            for i, letter in enumerate(word):
                score += LETTER_VALUES[letter]
        elif direction == 'down':
            for i, letter in enumerate(word):
                score += LETTER_VALUES[letter]
        return score

    def is_game_over(self):
        return all(player.get_rack_length() == 0 for player in self.players)

# Example usage:
game = Game()
human_player = Player(game.bag, is_human=True)
human_player.set_name("Human Player")
ai_player = AIPlayer(game.bag)
ai_player.set_name("AI Player")

game.add_player(human_player)
game.add_player(ai_player)

game.start_game()
