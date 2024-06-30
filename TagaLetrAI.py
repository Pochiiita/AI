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

# Adjust the path to your Tagalog dictionary CSV file as needed
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
        self.add_to_bag(Tile("A", LETTER_VALUES), 9)
        self.add_to_bag(Tile("B", LETTER_VALUES), 2)
        self.add_to_bag(Tile("C", LETTER_VALUES), 2)
        self.add_to_bag(Tile("D", LETTER_VALUES), 4)
        self.add_to_bag(Tile("E", LETTER_VALUES), 12)
        self.add_to_bag(Tile("F", LETTER_VALUES), 2)
        self.add_to_bag(Tile("G", LETTER_VALUES), 3)
        self.add_to_bag(Tile("H", LETTER_VALUES), 2)
        self.add_to_bag(Tile("I", LETTER_VALUES), 9)
        self.add_to_bag(Tile("J", LETTER_VALUES), 9)
        self.add_to_bag(Tile("K", LETTER_VALUES), 1)
        self.add_to_bag(Tile("L", LETTER_VALUES), 4)
        self.add_to_bag(Tile("M", LETTER_VALUES), 2)
        self.add_to_bag(Tile("N", LETTER_VALUES), 6)
        self.add_to_bag(Tile("O", LETTER_VALUES), 8)
        self.add_to_bag(Tile("P", LETTER_VALUES), 2)
        self.add_to_bag(Tile("Q", LETTER_VALUES), 1)
        self.add_to_bag(Tile("R", LETTER_VALUES), 6)
        self.add_to_bag(Tile("S", LETTER_VALUES), 4)
        self.add_to_bag(Tile("T", LETTER_VALUES), 6)
        self.add_to_bag(Tile("U", LETTER_VALUES), 4)
        self.add_to_bag(Tile("V", LETTER_VALUES), 2)
        self.add_to_bag(Tile("W", LETTER_VALUES), 2)
        self.add_to_bag(Tile("X", LETTER_VALUES), 1)
        self.add_to_bag(Tile("Y", LETTER_VALUES), 2)
        self.add_to_bag(Tile("Z", LETTER_VALUES), 1)
        self.add_to_bag(Tile("#", LETTER_VALUES), 2)
        shuffle(self.bag)


    def take_from_bag(self):
        if self.bag:
            return self.bag.pop()
        else:
            return None

    def get_remaining_tiles(self):
        return len(self.bag)

class Rack:
    def __init__(self, bag):
        self.rack = []
        self.bag = bag
        self.initialize()

    def add_to_rack(self):
        tile = self.bag.take_from_bag()
        if tile:
            self.rack.append(tile)

    def initialize(self):
        for _ in range(7):
            self.add_to_rack()

    def get_rack_str(self):
        return ", ".join(tile.get_letter() for tile in self.rack)

    def get_rack_arr(self):
        return self.rack

    def remove_from_rack(self, letter):
        for tile in self.rack:
            if tile.get_letter() == letter:
                self.rack.remove(tile)
                break

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
        depth = 1  # Reduced depth for quicker evaluation
        print(f"AI {self.get_name()} is generating a move...")

        all_possible_moves = self.get_all_possible_moves(board)
        print(f"Total possible moves: {len(all_possible_moves)}")

        for move in all_possible_moves:
            if self.is_valid_move(move, board):
                board.place_word(move[0], move[1], move[2], self)
                score = self.alpha_beta_pruning(board, depth, float('-inf'), float('inf'), True, players)
                board.remove_word(move[0], move[1], move[2])
                if score > best_score:
                    best_score = score
                    best_move = move
                print(f"Move: {move}, Score: {score}")

        if best_move is None:
            print("No valid moves found by AI.")
        else:
            print(f"Best move: {best_move} with score: {best_score}")

        return best_move

    def get_all_possible_moves(self, board):
        moves = []
        rack_letters = [tile.get_letter() for tile in self.rack.get_rack_arr()]
        for word in self.generate_valid_words(rack_letters):
            for row in range(15):
                for col in range(15):
                    if board.board[row][col] == ' ' and self.has_adjacent_tiles(row, col, board):
                        if col + len(word) <= 15:
                            moves.append((word, (row, col), 'right'))
                        if row + len(word) <= 15:
                            moves.append((word, (row, col), 'down'))
        return moves

    def generate_valid_words(self, rack_letters):
        from itertools import permutations
        valid_words_set = set()
        for length in range(1, len(rack_letters) + 1):
            for perm in permutations(rack_letters, length):
                word = ''.join(perm)
                if word in valid_words:
                    valid_words_set.add(word)
        return valid_words_set

    def has_adjacent_tiles(self, row, col, board):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            adj_row, adj_col = row + dr, col + dc
            if 0 <= adj_row < 15 and 0 <= adj_col < 15:
                if board.board[adj_row][adj_col] != ' ':
                    return True
        return False

    def is_valid_move(self, move, board):
        word, (row, col), direction = move
        if direction == 'right':
            if col + len(word) > 15:
                return False
        elif direction == 'down':
            if row + len(word) > 15:
                return False
        return True

    def alpha_beta_pruning(self, board, depth, alpha, beta, maximizing_player, players):
        if depth == 0:
            return self.evaluate_board(board, players)
        if maximizing_player:
            max_eval = float('-inf')
            for move in self.get_all_possible_moves(board):
                if self.is_valid_move(move, board):
                    board.place_word(move[0], move[1], move[2], self)
                    eval = self.alpha_beta_pruning(board, depth - 1, alpha, beta, False, players)
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
                    eval = self.alpha_beta_pruning(board, depth - 1, alpha, beta, True, players)
                    board.remove_word(move[0], move[1], move[2])
                    min_eval = min(min_eval, eval)
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break
            return min_eval

    def evaluate_board(self, board, players):
        return sum(player.get_score() for player in players)


class Board:
    def __init__(self):
        self.board = [[' ' for _ in range(15)] for _ in range(15)]

    def get_board(self):
        return self.board

    def place_word(self, word, position, direction, player):
        row, col = position
        score = 0
        for i, letter in enumerate(word):
            if direction == 'right':
                self.board[row][col + i] = letter
            elif direction == 'down':
                self.board[row + i][col] = letter
            player.rack.remove_from_rack(letter)
            score += LETTER_VALUES.get(letter, 0)
        player.increase_score(score)

    def remove_word(self, word, position, direction):
        row, col = position
        for i, letter in enumerate(word):
            if direction == 'right':
                self.board[row][col + i] = ' '
            elif direction == 'down':
                self.board[row + i][col] = ' '

    def is_valid_position(self, row, col):
        return 0 <= row < 15 and 0 <= col < 15

    def display(self):
        for row in self.board:
            print(' '.join(row))

class ScrabbleGame:
    def __init__(self):
        self.bag = Bag()
        self.board = Board()
        self.players = [Player(self.bag), AIPlayer(self.bag)]
        self.players[0].set_name("Player 1")
        self.players[1].set_name("AI")
        self.current_player_index = 0
        self.winner = None

    def get_current_player(self):
        return self.players[self.current_player_index]

    def next_turn(self):
        self.current_player_index = (self.current_player_index + 1) % len(self.players)

    def check_winner(self):
        for player in self.players:
            if player.get_rack_length() == 0:
                self.winner = player
                return True
        return False

    def play(self):
        while not self.check_winner():
            current_player = self.get_current_player()
            print(f"{current_player.get_name()}'s turn:")
            self.board.display()
            print(f"Rack: {current_player.get_rack_str()}")
            if current_player.is_human_player():
                word = input("Enter a word: ").strip().upper()
                row = int(input("Enter row (0-14): "))
                col = int(input("Enter column (0-14): "))
                direction = input("Enter direction (right/down): ").strip().lower()
                if self.is_valid_move(word, row, col, direction, current_player):
                    self.board.place_word(word, (row, col), direction, current_player)
                else:
                    print("Invalid move. Try again.")
            else:
                move = current_player.generate_move(self.board, self.players)
                if move:
                    self.board.place_word(move[0], move[1], move[2], current_player)
            self.next_turn()
        print(f"The winner is {self.winner.get_name()} with a score of {self.winner.get_score()}!")

    def is_valid_move(self, word, row, col, direction, player):
        if direction == 'right' and col + len(word) > 15:
            return False
        if direction == 'down' and row + len(word) > 15:
            return False
        for letter in word:
            if letter not in [tile.get_letter() for tile in player.get_rack_arr()]:
                return False
        return True

# Example usage:
game = ScrabbleGame()
game.play()
