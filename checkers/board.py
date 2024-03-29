from typing import Any
import pygame
from .constants import BLACK, ROWS, RED, SQUARE_SIZE, COLS, WHITE
from .piece import Piece


class Board:
    def __init__(self):
        self.board = []
        self.red_left = self.white_left = 12
        self.red_kings = self.white_kings = 0
        self.create_board()
        self.turns = 0

    def draw_squares(self, win):
        win.fill(BLACK)
        for row in range(ROWS):
            for col in range(row % 2, COLS, 2):
                pygame.draw.rect(win, RED, (row*SQUARE_SIZE,
                                 col * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    def move(self, piece, row, col):
        self.board[piece.row][piece.col], self.board[row][col] = self.board[row][col], self.board[piece.row][piece.col]
        piece.move(row, col)

        if row == ROWS - 1 or row == 0:
            if not piece.king:
                piece.make_king()
                if piece.color == WHITE:
                    self.white_kings += 1
                else:
                    self.red_kings += 1

        self.turns += 1

    def get_piece(self, row, col):
        return self.board[row][col]

    def create_board(self):
        for row in range(ROWS):
            self.board.append([])
            for col in range(COLS):
                if col % 2 == ((row + 1) % 2):
                    if row < 3:
                        self.board[row].append(Piece(row, col, WHITE))
                    elif row > 4:
                        self.board[row].append(Piece(row, col, RED))
                    else:
                        self.board[row].append(0)
                else:
                    self.board[row].append(0)

    def draw(self, win):
        self.draw_squares(win)
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece != 0:
                    piece.draw(win)

    def remove(self, pieces):
        for piece in pieces:
            self.board[piece.row][piece.col] = 0
            if piece != 0:
                if piece.color == RED:
                    self.red_left -= 1
                else:
                    self.white_left -= 1

    def winner(self):
        if self.red_left <= 0:
            return WHITE
        elif self.white_left <= 0:
            return RED
        # if turns exceeds 200, it is a draw
        elif self.turns > 200:
            return Any

        return None

    def get_valid_moves(self, piece):
        moves = {}
        left = piece.col - 1
        right = piece.col + 1
        row = piece.row

        if piece.color == RED or piece.king:
            moves.update(self._traverse_left(
                row - 1, max(row-3, -1), -1, piece.color, left))
            moves.update(self._traverse_right(
                row - 1, max(row-3, -1), -1, piece.color, right))
        if piece.color == WHITE or piece.king:
            moves.update(self._traverse_left(
                row + 1, min(row+3, ROWS), 1, piece.color, left))
            moves.update(self._traverse_right(
                row + 1, min(row+3, ROWS), 1, piece.color, right))

        return moves

    def _traverse_left(self, start, stop, step, color, left, skipped=[]):
        moves = {}
        last = []
        for r in range(start, stop, step):
            if left < 0:
                break

            current = self.board[r][left]
            if current == 0:
                if skipped and not last:
                    break
                elif skipped:
                    moves[(r, left)] = last + skipped
                else:
                    moves[(r, left)] = last

                if last:
                    if step == -1:
                        row = max(r-3, 0)
                    else:
                        row = min(r+3, ROWS)
                    moves.update(self._traverse_left(
                        r+step, row, step, color, left-1, skipped=last))
                    moves.update(self._traverse_right(
                        r+step, row, step, color, left+1, skipped=last))
                break
            elif current.color == color:
                break
            else:
                last = [current]

            left -= 1

        return moves

    def _traverse_right(self, start, stop, step, color, right, skipped=[]):
        moves = {}
        last = []
        for r in range(start, stop, step):
            if right >= COLS:
                break

            current = self.board[r][right]
            if current == 0:
                if skipped and not last:
                    break
                elif skipped:
                    moves[(r, right)] = last + skipped
                else:
                    moves[(r, right)] = last

                if last:
                    if step == -1:
                        row = max(r-3, 0)
                    else:
                        row = min(r+3, ROWS)
                    moves.update(self._traverse_left(
                        r+step, row, step, color, right-1, skipped=last))
                    moves.update(self._traverse_right(
                        r+step, row, step, color, right+1, skipped=last))
                break
            elif current.color == color:
                break
            else:
                last = [current]

            right += 1

        return moves

    def get_valid_pieces(self, player):
        all_pieces = []
        for row in self.board:
            for spot in row:
                if spot != 0:
                    if spot.color == player:
                        all_pieces.append(spot)
        return all_pieces

    def evaluate(self):
        # a draw leads to a board state of 0
        if self.turns > 200:
            return 0
        # white maximizes
        return self.white_left - self.red_left + self.white_kings - self.red_kings

    def evaluate1(self, params):
        # a draw leads to a board state of 0
        if self.turns > 200:
            return 0

        # calculate move flexibility- how many moves remain open
        white_moves = 0
        for piece in self.get_valid_pieces(WHITE):
            for _ in self.get_valid_moves(piece):
                white_moves += 1
        red_moves = 0
        for piece in self.get_valid_pieces(RED):
            for _ in self.get_valid_moves(piece):
                red_moves += 1

        # calculate board control- the number of squares that are threatened by
        # my pieces
        white_squares = set()
        for piece in self.get_valid_pieces(WHITE):
            for (row, col), _ in self.get_valid_moves(piece).items():
                white_squares.add((row, col))
        white_control = len(white_squares)
        red_squares = set()
        for piece in self.get_valid_pieces(RED):
            for (row, col), _ in self.get_valid_moves(piece).items():
                red_squares.add((row, col))
        red_control = len(red_squares)

        # calculate home row strength- how many of my pieces remain in the home
        # row
        white_home = 0
        for piece in self.get_valid_pieces(WHITE):
            if piece.row == 0:
                white_home += 1
        red_home = 0
        for piece in self.get_valid_pieces(RED):
            if piece.row == ROWS - 1:
                red_home += 1

        # calculate vulnerability- the number of pieces undefended
        undefended_white = set()
        for piece in self.get_valid_pieces(RED):
            for (row, col), skip in self.get_valid_moves(piece).items():
                if skip:
                    for s in skip:
                        undefended_white.add(s)
        white_vuln = len(undefended_white)
        undefended_red = set()
        for piece in self.get_valid_pieces(WHITE):
            for (row, col), skip in self.get_valid_moves(piece).items():
                if skip:
                    for s in skip:
                        undefended_red.add(s)
        red_vuln = len(undefended_red)

        return (
            (self.white_left - self.red_left)/1 +
            (self.white_kings - self.red_kings)*params[0]/4 +
            (white_moves - red_moves)*params[1]/4 +
            (white_control - red_control)*params[2]/4 +
            (red_vuln - white_vuln)*params[3]/4 +
            (white_home - red_home)*params[4]/4
        )
