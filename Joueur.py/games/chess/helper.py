from collections import namedtuple

# 4 Corners of the co-ordinates of the board representation
A1, H1, A8, H8 = 91, 98, 21, 28

# This function returns a board index using the given file and rank indices on the board
def board_index(file_index, rank_index):    
    file_index = ord(file_index.upper()) - 65
    rank_index = int(rank_index) - 1
    return A1 + file_index - (10 * rank_index)

# This function returns the file on board
def board_file(board_index):
    file_names = ["a", "b", "c", "d", "e", "f", "g", "h"]
    return file_names[(board_index % 10) - 1]

# This function returns rank on board
def board_rank(board_index):
    return 10 - (board_index // 10)

# Converts the given board index (21 - 98) to Standard Algebraic Notation
def convert_san(board_index):
    board = namedtuple('board', 'file rank')
    return board(board_file(board_index), board_rank(board_index))