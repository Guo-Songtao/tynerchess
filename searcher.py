import position as p
from definitions import *
from importlib import reload

reload(p)
INF = pow(10, 9) - 1


class Searcher:
    def __init__(self):
        self.pos: p.Position = p.Position()

    def setPos(self, fen: str):
        self.pos.init(fen)

    def setBegin(self):
        self.setPos(FEN_BEGIN)

    def search(
        self, pos: p.Position, depth: int, alpha: int = -INF, beta: int = INF, deepen: bool = False
    ) -> int:
        """
        return the score of the situation.
        """
        if depth == 0:
            if DEEPEN_SEARCH:
                if deepen:
                    return pos.score()
                else:
                    return self.search(pos, DEEPEN_DEPTH, alpha, beta, True)
            else:
                return pos.score()

        flg = True
        for mv in pos.allCaptures() if deepen else pos.allMoves():
            flg = False
            child_pos = pos.makeMove(mv)
            gameEnd = child_pos.gameEnd()
            if gameEnd:
                return gameEnd
            child_score = self.search(child_pos, depth - 1, alpha, beta, deepen)
            if pos.turn == TURN_W and child_score > alpha:  # max
                alpha = child_score
            elif pos.turn == TURN_B and child_score < beta:  # min
                beta = child_score
            if USE_AB and alpha >= beta:
                break
        if flg: # no move available at current position
            return pos.gameEnd()
        return alpha if pos.turn == TURN_W else beta

    #@timer
    def go(self, pos: p.Position, depth: int) -> p.Move:
        if depth < 1:
            raise Exception("Chessbot.go(): depth must be larger than 1!")

        alpha = -INF
        beta = INF
        best_move = None
        for mv in pos.allMoves():
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
