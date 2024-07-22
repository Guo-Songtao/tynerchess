import position as p
from definitions import *
from typing import Optional
from importlib import reload

reload(p)
INF = pow(10, 9) - 1

USE_AB = False


class Searcher:
    def __init__(self):
        self.pos: p.Position = p.Position()

    def setPos(self, fen: str):
        self.pos.readFEN(fen)

    def setBegin(self):
        self.setPos(FEN_BEGIN)

    def search(
        self, pos: p.Position, depth: int, alpha: int = -INF, beta: int = INF
    ) -> int:
        """
        return the score of the situation.
        """
        if depth == 0:
            return pos.calcScore()

        for mv in pos.allLeagalMoves():
            child_score = self.search(pos.makeMove(mv), depth - 1, alpha, beta)
            if pos.turn == TURN_W and child_score > alpha:  # max
                alpha = child_score
            elif pos.turn == TURN_B and child_score < beta:  # min
                beta = child_score
            if USE_AB and alpha >= beta:
                break
        return alpha if pos.turn == TURN_W else beta

    @timer
    def go(self, pos: p.Position, depth: int) -> p.Move:
        if depth < 1:
            raise Exception("Chessbot.go(): depth must be larger than 1!")

        alpha = -INF
        beta = INF
        best_move = None
        for mv in pos.allLeagalMoves():
            child_score = self.search(pos.makeMove(mv), depth - 1, alpha, beta)
            if pos.turn == TURN_W and child_score > alpha:  # max
                alpha = child_score
                best_move = mv
            elif pos.turn == TURN_B and child_score < beta:  # min
                beta = child_score
                best_move = mv
            if USE_AB and alpha >= beta:
                break

        return best_move
