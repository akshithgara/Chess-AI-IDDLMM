# This is where you build your AI for the Chess game.

from joueur.base_ai import BaseAI

# <<-- Creer-Merge: imports -->> - Code you add between this comment and the end comment will be preserved between Creer re-runs.
import random
from games.chess.state import State
from games.chess.helper import convert_san, board_index



# This function returns a table like formatted string by parsing the given fen string 
def print_from_fen(fen, us):

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


# This function returns a state object by parsing the given fen string
def fen_to_position(fen_string):
    # generate a State object from a FEN string
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
        enpassant = board_index(enpassant[0], enpassant[1])
    else:
        enpassant = 0

    # Position(board score wc bc ep kp depth)
    if player == 'w':
        return State(board_out, 0, wc, bc, enpassant, 0, 0, None)
    else:
        return State(board_out, 0, wc, bc, enpassant, 0, 0, None).rotate()
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
        validMoveList = [] # A list that stores all the valid moves for a given state

        # Loops through all the probable valid moves generated by gen_moves function
        for move in self.board.gen_moves(): 
            (piece_index, move_index) = (move)  
            if self.player.color == "black":
                piece_index = 119 - piece_index
                move_index = 119 - move_index
            initial = convert_san(piece_index).file + str(convert_san(piece_index).rank)
            final = convert_san(move_index).file + str(convert_san(move_index).rank)
            totalMove = initial + final
            # print("expanding", totalMove)
            next_board = self.board.move(move)
            # print("next", next_board)
            if not next_board.check_check():
                validMoveList.append(totalMove)


        # print(validMoveList)
        randomMove = random.choice(validMoveList)
        # print(randomMove)
        # print(validMoveList)
        return randomMove
        # <<-- /Creer-Merge: makeMove -->>

    # <<-- Creer-Merge: functions -->> - Code you add between this comment and the end comment will be preserved between Creer re-runs.
    def update_board(self):
        # update current board state by converting current FEN to State object
        self.board = fen_to_position(self.game.fen)


    # <<-- /Creer-Merge: functions -->>
