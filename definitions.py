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

random.seed("lucky lucky")
#'e' for enpassant
Z_HASH_BOARD: list[dict[str, int]] = [{piece: random.randint(-2**127, 2**127 + 1) for piece in "PKQRBNpkqrbne0"} for sq in range(120)]
Z_HASH_CASTLE: dict[bool, dict[str, int]] = {turn: {side: random.randint(-2**127, 2**127 + 1) for side in "kq"} for turn in [True, False]}
Z_HASH_TURN: dict[bool, int] = {turn: random.randint(-2**127, 2**127 + 1) for turn in [True, False]}


def timer(func):
    def funcWrapper(*args, **kwargs):
        from time import time

        time_start = time()
        result = func(*args, **kwargs)
        time_end = time()
        time_used = time_end - time_start
        print("time used by {}: {}s".format(func.__name__, time_used))
        return result

    return funcWrapper


USE_SELF_CACHE = False
USE_AB = True
TEST_DEPTH = 4

MEM_TIME_GAP = 0.01
