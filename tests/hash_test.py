import random
from itertools import product
from importlib import reload

from definitions import *
import position as p

reload(p)


def random_fen():
    pos = p.Position()
    pos.init()
    for sq in ITER_BOARD:
        pos.board[sq] = PIECES[random.randint(0, len(PIECES) - 1)]
    pos.turn = [TURN_W, TURN_B][random.randint(0, 1)]
    for turn, side in product((TURN_W, TURN_B), ("k", "q")):
        pos.canCastle[turn][side] = [True, False][random.randint(0, 1)]
    return pos.fen()


def main(fen: str = None):
    if not fen:
        flg = True
        for _ in range(100000):
            rfen = random_fen()
            pos = p.Position()
            pos.init(rfen)
            moves = pos.allLeagalMoves()
            try:
                mv = moves[random.randint(0, len(moves) - 1)]
            except Exception:
                continue
            p_mv = pos.makeMove(mv)
            p_fen = p.Position()
            p_fen.init(p_mv.fen())
            if not (p_mv == p_fen and hash(p_mv) == hash(p_fen)):
                flg = False
                print(rfen, mv)
        print(flg)
    else:
        flg = True
        pos = p.Position()
        pos.init(fen)
        moves = pos.allLeagalMoves()
        for mv in moves:
            try:
                p_mv = pos.makeMove(mv)
            except Exception as exc:
                print(pos)
                raise exc
            p_fen = p.Position()
            p_fen.init(p_mv.fen())
            if not (p_mv == p_fen and hash(p_mv) == hash(p_fen)):
                flg = False
                print(fen, mv)
                print(pos.fen())
                print("-----------")
        print(flg)


if __name__ == "__main__":
    main("r1bqk2r/pppp1p1p/2n2n2/2b1p3/1PB1P1p1/2N2N2/P1PPQPPP/R1B1K2R w KQkq - 0 7")
