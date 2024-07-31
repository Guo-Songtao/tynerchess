import random

SAFEMODE = True

INF = pow(10, 9) - 1
TURN_W = True
TURN_B = False

PIECES_B = "pnbrqk"
PIECES_W = "PNBRQK"
PIECES = PIECES_B + PIECES_W
EDGE = "+"
BLANK = "0"
N, S, W, E = -10, +10, -1, +1
DIRECTIONS = (N, S, E, W, N + E, N + W, S + E, S + W)
DIRS_PIECES = {
    "P": (N, N * 2, N + W, N + E),
    "p": (S, S * 2, S + W, S + E),
    "N": (
        2 * N + W,
        2 * N + E,
        2 * S + W,
        2 * S + E,
        N + 2 * E,
        N + 2 * W,
        S + 2 * E,
        S + 2 * W,
    ),
    "B": (N + W, N + E, S + W, S + E),
    "R": (N, S, W, E),
    "Q": (N, S, W, E, N + W, N + E, S + W, S + E),
    "K": (N, S, W, E, N + W, N + E, S + W, S + E),
}
for piece in "nbrqk":
    DIRS_PIECES[piece] = DIRS_PIECES[piece.upper()]

FEN_BEGIN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

ITER_BOARD = tuple((21 + i + j * 10 for i in range(8) for j in range(8)))
ITER_EDGE = tuple(
    10 * m + n for m in range(12) for n in range(10) if 10 * m + n not in ITER_BOARD
)

random.seed("lucky lucky")


#'e' for enpassant
def rand_hash():
    return random.randint(-(2**127), 2**127 + 1)


Z_HASH_BOARD: list[dict[str, int]] = [
    {piece: rand_hash() for piece in "PKQRBNpkqrbne" + BLANK} for sq in range(120)
]
for d in Z_HASH_BOARD:
    d[BLANK] = 0
Z_HASH_CASTLE: dict[bool, dict[str, dict[bool, int]]] = {
    turn: {side: {val: rand_hash() for val in (True, False)} for side in "kq"}
    for turn in [TURN_W, TURN_B]
}
Z_HASH_TURN: dict[bool, int] = {TURN_W: 0, TURN_B: rand_hash()}


def timer(func):
    def funcWrapper(*args, **kwargs):
        from time import time

        time_start = time()
        result = func(*args, **kwargs)
        time_end = time()
        time_used = time_end - time_start
        print("time used by {}: {}s".format(func.__name__, time_used))
        return result
    funcWrapper.__name__ = func.__name__
    return funcWrapper


USE_Z_HASH = True
USE_SELF_CACHE = True
USE_AB = True
TEST_DEPTH = 3
TEST_FEN = "4r1k1/1pqn1pbp/p5p1/3B4/2Q2P2/1P4PP/P4P2/2BR2K1 b - - 2 24"
DEEPEN_SEARCH = True
DEEPEN_DEPTH = 3

MEM_TIME_GAP = 0.01
