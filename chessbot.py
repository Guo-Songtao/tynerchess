import position as p
from definitions import *
from typing import Optional
from importlib import reload

reload(p)
INF = pow(10, 9) - 1


class Chessbot:
    def __init__(self):
        self.pos: p.Position = p.Position()

    def setPos(self, fen: str):
        self.pos.readFEN(fen)

    def setBegin(self):
        self.setPos(FEN_BEGIN)

    def search(self, pos: p.Position, depth: int) -> int:
        """
        return the score of the situation
        """
        if depth == 0:
            return pos.calcScore()

        cmp = (
            (lambda rec, new: rec < new)
            if pos.turn == TURN_W
            else (lambda rec, new: rec > new)
        )
        recordScore = -INF if pos.turn == TURN_W else INF
        # make (factor * score) bigger
        for mv in pos.allLeagalMoves():
            score = self.search(pos.makeMove(mv), depth - 1)
            if cmp(recordScore, score):
                recordScore = score

        return recordScore

    @timer
    def go(self, pos: p.Position, depth: int) -> p.Move:
        if depth < 1:
            raise Exception("Chessbot.go(): depth must be larger than 1!")

        cmp = (
            (lambda rec, new: rec < new)
            if pos.turn == TURN_W
            else (lambda rec, new: rec > new)
        )
        recordScore = -INF if pos.turn == TURN_W else INF
        recordMove = None
        # make (factor * score) bigger
        for mv in pos.allLeagalMoves():
            score = self.search(pos.makeMove(mv), depth - 1)
            if cmp(recordScore, score):
                recordScore = score
                recordMove = mv

        return recordMove
