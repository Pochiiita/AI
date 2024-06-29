import csv
from random import shuffle

# Keeps track of the score-worth of each letter-tile.
LETTER_VALUES = {"A": 1, "B": 3, "C": 3, "D": 2, "E": 1, "F": 4, "G": 2, "H": 4, "I": 1, "J": 1, "K": 5,
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

class AIPlayer(Player):
    def __init__(self, bag):
        super().__init__(bag, is_human=False)

    def generate_move(self, board):
        best_move = None
        best_score = float('-inf')
        depth = 3  # Depth of search for the alpha-beta pruning
        for move in self.get_all_possible_moves(board):
            score = self.alpha_beta_pruning(board, depth, float('-inf'), float('inf'), True)
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
                        moves.append((tile.get_letter(), (row, col), 'right'))
        return moves

    def alpha_beta_pruning(self, board, depth, alpha, beta, maximizing_player):
        if depth == 0:
            return self.heuristic_evaluation(board)
        if maximizing_player:
            max_eval = float('-inf')
            for move in self.get_all_possible_moves(board):
                board.place_word(*move, self)
                eval = self.alpha_beta_pruning(board, depth-1, alpha, beta, False)
                board.remove_word(*move)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for move in self.get_all_possible_moves(board):
                board.place_word(*move, self)
                eval = self.alpha_beta_pruning(board, depth-1, alpha, beta, True)
                board.remove_word(*move)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    def heuristic_evaluation(self, board):
        ai_score = self.get_score()
        human_score = next(player.get_score() for player in players if player.is_human_player())
        return ai_score - human_score

class Board:
    def __init__(self):
        self.board = [[' ' for _ in range(15)] for _ in range(15)]

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
        TRIPLE_WORD_SCORE = ((0,0), (7, 0), (14,0), (0, 7), (14, 7), (0, 14), (7, 14), (14,14))
        DOUBLE_WORD_SCORE = ((1,1), (2,2), (3,3), (4,4), (1, 13), (2, 12), (3, 11), (4, 10), (13, 1), (12, 2), (11, 3), (10, 4), (13,13), (12, 12), (11,11), (10,10))
        TRIPLE_LETTER_SCORE = ((1,5), (1, 9), (5,1), (5,5), (5,9), (5,13), (9,1), (9,5), (9,9), (9,13), (13, 5), (13,9))
        DOUBLE_LETTER_SCORE = ((0, 3), (0,11), (2,6), (2,8), (3,0), (3,7), (3,14), (6,2), (6,6), (6,8), (6,12), (7,3), (7,11), (8,2), (8,6), (8,8), (8, 12), (11,0), (11,7), (11,14), (12,6), (12,8), (14, 3), (14, 11))

        for coordinate in TRIPLE_WORD_SCORE:
            self.board[coordinate[0]][coordinate[1]] = "TWS"
        for coordinate in TRIPLE_LETTER_SCORE:
            self.board[coordinate[0]][coordinate[1]] = "TLS"
        for coordinate in DOUBLE_WORD_SCORE:
            self.board[coordinate[0]][coordinate[1]] = "DWS"
        for coordinate in DOUBLE_LETTER_SCORE:
            self.board[coordinate[0]][coordinate[1]] = "DLS"

    def place_word(self, word, location, direction, player):
        global premium_spots
        premium_spots = []
        direction = direction.lower()
        word = word.upper()

        if direction.lower() == "right":
            for i in range(len(word)):
                if self.board[location[0]][location[1]+i] != "   ":
                    premium_spots.append((word[i], self.board[location[0]][location[1]+i]))
                self.board[location[0]][location[1]+i] = " " + word[i] + " "

        elif direction.lower() == "down":
            for i in range(len(word)):
                if self.board[location[0]][location[1]+i] != "   ":
                    premium_spots.append((word[i], self.board[location[0]][location[1]+i]))
                self.board[location[0]+i][location[1]] = " " + word[i] + " "

        for letter in word:
            for tile in player.get_rack_arr():
                if tile.get_letter() == letter:
                    player.rack.remove_from_rack(tile)
        player.rack.replenish_rack()

class Word:
    def __init__(self, word, location, player, direction, board):
        self.word = word.upper()
        self.location = location
        self.player = player
        self.direction = direction
        self.board = board

    def check_word(self):
        global valid_words
        if self.word not in valid_words:
            return "Word is not valid."
        return True

    def set_word(self, word):
        self.word = word.upper()

    def set_location(self, location):
        self.location = location

    def set_direction(self, direction):
        self.direction = direction

    def get_word(self):
        return self.word

    def calculate_word_score(self):
        word_score = sum(LETTER_VALUES.get(letter, 0) for letter in self.word)
        self.player.increase_score(word_score)

def turn(player, board, bag):
    global round_number, players, skipped_turns

    if skipped_turns < 6 or (player.rack.get_rack_length() == 0 and bag.get_remaining_tiles() == 0):
        print("\nRound " + str(round_number) + ": " + player.get_name() + "'s turn \n")
        print(board.get_board(players))
        print("\n" + player.get_name() + "'s Letter Rack: " + player.get_rack_str())

    if player.is_human_player():
        word_to_play = input("Word to play: ")
        col = int(input("Column number: "))
        row = int(input("Row number: "))
        location = [row, col]
        direction = input("Direction of word (right or down): ")
    else:
        word_to_play, location, direction = player.generate_move(board)

    word = Word(word_to_play, location, player, direction, board.board)
    checked = word.check_word()
    while checked != True:
        print(checked)
        if player.is_human_player():
            word_to_play = input("Word to play: ")
            word.set_word(word_to_play)
            col = int(input("Column number: "))
            row = int(input("Row number: "))
            location = [row, col]
            word.set_location(location)
            direction = input("Direction of word (right or down): ")
            word.set_direction(direction)
        else:
            word_to_play, location, direction = player.generate_move(board)
        checked = word.check_word()

    if word.get_word() == "":
        print("Your turn has been skipped.")
        skipped_turns += 1
    else:
        board.place_word(word_to_play, location, direction, player)
        word.calculate_word_score()
        skipped_turns = 0

    print("\n" + player.get_name() + "'s score is: " + str(player.get_score()))

    if players.index(player) != (len(players) - 1):
        player = players[players.index(player) + 1]
    else:
        player = players[0]
        round_number += 1

    turn(player, board, bag)
    end_game()

def start_game():
    global round_number, players, skipped_turns
    board = Board()
    bag = Bag()

    print("\n\t\t\tWelcome to TagaLetrAI!")
    human_player = Player(bag)
    human_player.set_name(input("\tPlease enter your name: "))

    ai_player = AIPlayer(bag)
    ai_player.set_name("AI")

    players = [human_player, ai_player]

    round_number = 1
    skipped_turns = 0
    current_player = players[0]
    turn(current_player, board, bag)

def end_game():
    global players
    highest_score = 0
    winning_player = ""
    for player in players:
        if player.get_score() > highest_score:
            highest_score = player.get_score()
            winning_player = player.get_name()
    print("GAME OVER! " + winning_player + ", you have won!")

    if input("\nPlay again? (y/n)").upper() == "Y":
        start_game()

# Start the game
start_game()
