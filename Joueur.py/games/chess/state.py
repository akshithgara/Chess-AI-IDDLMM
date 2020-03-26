from collections import namedtuple
from itertools import count

A1, H1, A8, H8 = 91, 98, 21, 28
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


class State(namedtuple('State', 'board score wc bc ep kp depth captured')):
    """ A state of a chess game
    board -- a 120 char representation of the board
    score -- the board evaluation
    wc -- the castling rights, [west/queen side, east/king side]
    bc -- the opponent castling rights, [west/king side, east/queen side]
    ep - the en passant square
    kp - the king passant square
    depth - the node depth of the State
    captured - the piece that was captured as the result of the last move
    """

    def gen_moves(self):
        for i, p in enumerate(self.board):
            # i - initial State index
            # p - piece code

            # if the piece doesn't belong to us, skip it
            if not p.isupper(): continue
            for d in directions[p]:
                # d - potential action for a given piece
                for j in count(i + d, d):
                    # j - final State index
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
        return State(
            self.board[::-1].swapcase(), -self.score, self.bc, self.wc,
            119 - self.ep if self.ep else 0,
            119 - self.kp if self.kp else 0, self.depth, None)

    def nullmove(self):
        # Like rotate, but clears ep and kp
        return State(
            self.board[::-1].swapcase(), -self.score,
            self.bc, self.wc, 0, 0, self.depth + 1, None)

    def move(self, move):
        # i - original State index
        # j - final State index
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
        # Rotate the returned State so it's ready for the next player
        return State(board, 0, wc, bc, ep, kp, depth, q.upper()).rotate()

    def is_check(self):
        # returns if the state represented by the current State is check
        for move in self.gen_moves():
            i, j = move
            p, q = self.board[i], self.board[j]
            # opponent can take our king
            if q == 'k':
                return True
        return False