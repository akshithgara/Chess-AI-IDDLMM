# This is where you build your AI for the Chess game.

from joueur.base_ai import BaseAI

# <<-- Creer-Merge: imports -->> - Code you add between this comment and the end comment will be preserved between Creer re-runs.
from math import inf
from timeit import default_timer as timer
from collections import namedtuple, defaultdict
from itertools import count
from random import getrandbits
from operator import xor
import re


A1, H1, A8, H8 = 91, 98, 21, 28
initial = (
    '         \n'  # 0 -  9
    '         \n'  # 10 - 19
    ' rnbqkbnr\n'  # 20 - 29
    ' pppppppp\n'  # 30 - 39
    ' ........\n'  # 40 - 49
    ' ........\n'  # 50 - 59
    ' ........\n'  # 60 - 69
    ' ........\n'  # 70 - 79
    ' PPPPPPPP\n'  # 80 - 89
    ' RNBQKBNR\n'  # 90 - 99
    '         \n'  # 100 -109
    '         \n'  # 110 -119
)

N, E, S, W = -10, 1, 10, -1

# valid moves for each piece
directions = {
    'P': (N, N + N, N + W, N + E),
    'N': (N + N + E, E + N + E, E + S + E, S + S + E, S + S + W, W + S + W, W + N + W, N + N + W),
    'B': (N + E, S + E, S + W, N + W),
    'R': (N, E, S, W),
    'Q': (N, E, S, W, N + E, S + E, S + W, N + W),
    'K': (N, E, S, W, N + E, S + E, S + W, N + W)
}

piece_values = {
    'P': 1,
    'N': 3,
    'B': 3,
    'R': 5,
    'Q': 9,
    'K': 200
}

z_indicies = {
    'P': 1,
    'N': 2,
    'B': 3,
    'R': 4,
    'Q': 5,
    'K': 6,
    'p': 7,
    'n': 8,
    'b': 9,
    'r': 10,
    'q': 11,
    'k': 12
}

def pretty_fen(fen, us):
    """
    Pretty formats an FEN string to a human readable string.
    For more information on FEN (Forsyth-Edwards Notation) strings see:
    https://wikipedia.org/wiki/Forsyth%E2%80%93Edwards_Notation
    """

    # split the FEN string up to help parse it
    split = fen.split(' ')
    first = split[0]  # the first part is always the board locations

    side_to_move = split[1]  # always the second part for side to move
    us_or_them = 'us' if side_to_move == us[0] else 'them'

    fullmove = split[5]  # always the sixth part for the full move

    lines = first.split('/')
    strings = ['Move: {}\nSide to move: {} ({})\n   +-----------------+'.format(
        fullmove, side_to_move, us_or_them
    )]

    for i, line in enumerate(lines):
        strings.append('\n {} |'.format(8 - i))
        for char in line:
            try:
                char_as_number = int(char)
                # it is a number, so that many blank lines
                strings.append(' .' * char_as_number)
            except:
                strings.append(' ' + char)

        strings.append(' |')
    strings.append('\n   +-----------------+\n     a b c d e f g h\n')

    return ''.join(strings)

class Position(namedtuple('Position', 'board score wc bc ep kp depth captured')):
    """ A state of a chess game
    board -- a 120 char representation of the board
    score -- the board evaluation
    wc -- the castling rights, [west/queen side, east/king side]
    bc -- the opponent castling rights, [west/king side, east/queen side]
    ep - the en passant square
    kp - the king passant square
    depth - the node depth of the position
    captured - the piece that was captured as the result of the last move
    """

    def gen_moves(self):
        for i, p in enumerate(self.board):
            # i - initial position index
            # p - piece code

            # if the piece doesn't belong to us, skip it
            if not p.isupper(): continue
            for d in directions[p]:
                # d - potential action for a given piece
                for j in count(i + d, d):
                    # j - final position index
                    # q - occupying piece code
                    q = self.board[j]
                    # Stay inside the board, and off friendly pieces
                    if q.isspace() or q.isupper(): break
                    # Pawn move, double move and capture
                    if p == 'P' and d in (N, N + N) and q != '.': break
                    if p == 'P' and d == N + N and (i < A1 + N or self.board[i + N] != '.'): break
                    if p == 'P' and d in (N + W, N + E) and q == '.' and j not in (self.ep, self.kp): break
                    # Move it
                    yield (i, j)
                    # Stop non-sliders from sliding and sliding after captures
                    if p in 'PNK' or q.islower(): break
                    # Castling by sliding rook next to king
                    if i == A1 and self.board[j + E] == 'K' and self.wc[0]: yield (j + E, j + W)
                    if i == H1 and self.board[j + W] == 'K' and self.wc[1]: yield (j + W, j + E)

    def rotate(self):
        # Rotates the board, preserving enpassant
        # Allows logic to be reused, as only one board configuration must be considered
        return Position(
            self.board[::-1].swapcase(), -self.score, self.bc, self.wc,
            119 - self.ep if self.ep else 0,
            119 - self.kp if self.kp else 0, self.depth, None)

    def nullmove(self):
        # Like rotate, but clears ep and kp
        return Position(
            self.board[::-1].swapcase(), -self.score,
            self.bc, self.wc, 0, 0, self.depth + 1, None)

    def move(self, move):
        # i - original position index
        # j - final position index
        i, j = move
        # p - piece code of moving piece
        # q - piece code at final square
        p, q = self.board[i], self.board[j]
        # put replaces string character at i with character p
        put = lambda board, i, p: board[:i] + p + board[i + 1:]
        # copy variables and reset eq and kp and increment depth
        board = self.board
        wc, bc, ep, kp, depth = self.wc, self.bc, 0, 0, self.depth + 1
        # score = self.score + self.value(move)
        # perform the move
        board = put(board, j, board[i])
        board = put(board, i, '.')
        # update castling rights, if we move our rook or capture the opponent's rook
        if i == A1: wc = (False, wc[1])
        if i == H1: wc = (wc[0], False)
        if j == A8: bc = (bc[0], False)
        if j == H8: bc = (False, bc[1])
        # Castling Logic
        if p == 'K':
            wc = (False, False)
            if abs(j - i) == 2:
                kp = (i + j) // 2
                board = put(board, A1 if j < i else H1, '.')
                board = put(board, kp, 'R')
        # Pawn promotion, double move, and en passant capture
        if p == 'P':
            if A8 <= j <= H8:
                # Promote the pawn to Queen
                board = put(board, j, 'Q')
            if j - i == 2 * N:
                ep = i + N
            if j - i in (N + W, N + E) and q == '.':
                board = put(board, j + S, '.')
        # Rotate the returned position so it's ready for the next player
        return Position(board, 0, wc, bc, ep, kp, depth, q.upper()).rotate()

    def value(self):
        score = 0
        # evaluate material advantage
        for k, p in enumerate(self.board):
            # k - position index
            # p - piece code
            if p.isupper(): score += piece_values[p]
            if p.islower(): score -= piece_values[p.upper()]
        return score

    def is_check(self):
        # returns if the state represented by the current position is check
        op_board = self.nullmove()
        for move in op_board.gen_moves():
            i, j = move
            p, q = op_board.board[i], op_board.board[j]
            # opponent can take our king
            if q == 'k':
                return True
        return False

####################################
# square formatting helper functions
####################################

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


def fen_to_position(fen_string):
    # generate a Position object from a FEN string
    board, player, castling, enpassant, halfmove, move = fen_string.split()
    board = board.split('/')
    board_out = '         \n         \n'
    for row in board:
        board_out += ' '
        for piece in row:
            if piece.isdigit():
                for _ in range(int(piece)):
                    board_out += '.'
            else:
                board_out += piece
        board_out += '\n'
    board_out += '         \n         \n'

    wc = (False, False)
    bc = (False, False)
    if 'K' in castling: wc = (True, wc[1])
    if 'Q' in castling: wc = (wc[0], True)
    if 'k' in castling: bc = (True, bc[1])
    if 'q' in castling: bc = (bc[0], True)

    if enpassant != '-':
        enpassant = square_index(enpassant[0], enpassant[1])
    else:
        enpassant = 0

    # Position(board score wc bc ep kp depth)
    if player == 'w':
        return Position(board_out, 0, wc, bc, enpassant, 0, 0, None)
    else:
        return Position(board_out, 0, wc, bc, enpassant, 0, 0, None).rotate()
# <<-- /Creer-Merge: imports -->>

class AI(BaseAI):
    """ The AI you add and improve code inside to play Chess. """

    @property
    def game(self) -> 'games.chess.game.Game':
        """games.chess.game.Game: The reference to the Game instance this AI is playing.
        """
        return self._game  # don't directly touch this "private" variable pls

    @property
    def player(self) -> 'games.chess.player.Player':
        """games.chess.player.Player: The reference to the Player this AI controls in the Game.
        """
        return self._player  # don't directly touch this "private" variable pls

    def get_name(self) -> str:
        """This is the name you send to the server so your AI will control the player named this string.

        Returns:
            str: The name of your Player.
        """
        # <<-- Creer-Merge: get-name -->> - Code you add between this comment and the end comment will be preserved between Creer re-runs.
        return "TWD"  # REPLACE THIS WITH YOUR TEAM NAME
        # <<-- /Creer-Merge: get-name -->>

    def start(self) -> None:
        """This is called once the game starts and your AI knows its player and game. You can initialize your AI here.
        """
        # <<-- Creer-Merge: start -->> - Code you add between this comment and the end comment will be preserved between Creer re-runs.
        self.board = fen_to_position(self.game.fen)
        self.transposition_table = dict()
        # <<-- /Creer-Merge: start -->>

    def game_updated(self) -> None:
        """This is called every time the game's state updates, so if you are tracking anything you can update it here.
        """
        # <<-- Creer-Merge: game-updated -->> - Code you add between this comment and the end comment will be preserved between Creer re-runs.
        self.update_board()
        # <<-- /Creer-Merge: game-updated -->>

    def end(self, won: bool, reason: str) -> None:
        """This is called when the game ends, you can clean up your data and dump files here if need be.

        Args:
            won (bool): True means you won, False means you lost.
            reason (str): The human readable string explaining why your AI won or lost.
        """
        # <<-- Creer-Merge: end -->> - Code you add between this comment and the end comment will be preserved between Creer re-runs.
        # replace with your end logic
        # <<-- /Creer-Merge: end -->>

    def make_move(self) -> str:
        """This is called every time it is this AI.player's turn to make a move.

        Returns:
            str: A string in Universal Chess Inferface (UCI) or Standard Algebraic Notation (SAN) formatting for the move you want to make. If the move is invalid or not properly formatted you will lose the game.
        """
        # <<-- Creer-Merge: makeMove -->> - Code you add between this comment and the end comment will be preserved between Creer re-runs.
        # Put your game logic here for makeMove
        print(self.board)
        print(pretty_fen(self.game.fen, self.player.color))
        for move in self.board.gen_moves():
            (piece_index, move_index) = (move)
            print(square_san(piece_index), square_san(move_index))


        return ""
        # <<-- /Creer-Merge: makeMove -->>

    # <<-- Creer-Merge: functions -->> - Code you add between this comment and the end comment will be preserved between Creer re-runs.
    def update_board(self):
        # update current board state by converting current FEN to Position object
        self.board = fen_to_position(self.game.fen)


    # <<-- /Creer-Merge: functions -->>
