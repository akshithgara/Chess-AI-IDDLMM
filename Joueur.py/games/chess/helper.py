####################################
# square formatting helper functions
####################################
from collections import namedtuple

A1, H1, A8, H8 = 91, 98, 21, 28
def square_index(file_index, rank_index):
    # Gets a square index by file and rank index
    file_index = ord(file_index.upper()) - 65
    rank_index = int(rank_index) - 1
    return A1 + file_index - (10 * rank_index)


def square_file(square_index):
    file_names = ["a", "b", "c", "d", "e", "f", "g", "h"]
    return file_names[(square_index % 10) - 1]


def square_rank(square_index):
    return 10 - (square_index // 10)


def square_san(square_index):
    # convert square index (21 - 98) to Standard Algebraic Notation
    square = namedtuple('square', 'file rank')
    return square(square_file(square_index), square_rank(square_index))