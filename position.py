from typing import Optional, Iterator
from itertools import product, chain
from functools import cache
from pst import PST

from definitions import *
import timer.dicted_timer as dt


def isOnBoard(n: int) -> bool:
    i = n // 10 - 2  # row
    j = n % 10 - 1  # column
    if 0 <= i < 8 and 0 <= j < 8:
        ans = True
    else:
        ans = False
    return ans


def sq2alg(sq: int) -> str:
    if sq == None:
        return None
    alg = chr(ord("a") - 1 + sq % 10) + str(10 - sq // 10)
    if SAFEMODE and not (alg[0] in "abcdefgh" and alg[1] in "12345678"):
        raise Exception("squareToAlge: not on the board!")
    return alg


def alg2sq(alg: str) -> int:
    if SAFEMODE and not (alg[0] in "abcdefgh" and alg[1] in "12345678"):
        raise Exception("algeToSquare: not on the board!")
    sq = 10 * (10 - int(alg[1])) + ord(alg[0]) - ord("a") + 1
    return sq


def sq2cnt(sq: int) -> int:
    return sq % 10 - 1 + 8 * (sq // 10 - 2)


def cnt2sq(cnt: int) -> int:
    return cnt % 8 + 1 + 10 * (cnt // 8 + 2)


local_cache = dict()
def cache_position(func):
    local_cache[func.__name__] = dict()

    def func_wrapper(pos):
        zob = pos.zobrist_hash()
        if zob in local_cache[func.__name__].keys():
            ans = local_cache[func.__name__][zob]
        else:
            ans = func(pos)
            local_cache[func.__name__][zob] = ans
        return ans

    func_wrapper.__name__ = func.__name__
    return func_wrapper
if USE_SELF_CACHE:
    cache = cache_position


class Move:
    """
    attributes: fro(int), to(int)
    methods: __init__(fro, end), __repr__()
    """

    def __init__(self, fro=-1, end=-1):
        self.fro = fro
        self.to = end

    def __repr__(self) -> str:
        return "Move[{}, {}]".format(sq2alg(self.fro), sq2alg(self.to))

    def __eq__(self, value) -> bool:
        return self.fro == value.fro and self.to == value.to

    def __hash__(self) -> int:
        return self.fro * 120 + self.to


class Position:
    def init(self, fen: str = FEN_BEGIN):
        sfen: list[str] = fen.split(" ")

        # board
        self.board = [BLANK] * 120
        for sq in ITER_EDGE:
            self.board[sq] = EDGE
        for i, line in enumerate(sfen[0].split("/")):
            j = 1
            for c in line:
                if c.isalpha():
                    self.board[i * 10 + j + 20] = c
                    j += 1
                else:
                    j += int(c)

        # turn, canCastle, enPassant, mateSteps, numMoves
        self.turn: bool = TURN_W if sfen[1] == "w" else TURN_B
        self.canCastle: dict[str, dict[str, bool]] = {
            TURN_W: {"k": "K" in sfen[2], "q": "Q" in sfen[2]},
            TURN_B: {"k": "k" in sfen[2], "q": "q" in sfen[2]},
        }  # canCastle[turn][side_of_board] = True/False
        self.enPassant: Optional[int] = None if sfen[3] == "-" else alg2sq(sfen[3])
        self.mateSteps = int(sfen[4])
        self.numMoves = int(sfen[5])

        self.zob_hash_val = None
        self.score_val = None
        self.zobrist_hash()
        self.calcScore()
        return self

    def __init__(self, fen: str = None):
        pass

    def deepcopy(self):
        new: Position = Position()
        new.board = []
        new.board.extend(self.board)
        new.turn = self.turn
        new.canCastle = {
            TURN_W: {
                "k": self.canCastle[TURN_W]["k"],
                "q": self.canCastle[TURN_W]["q"],
            },
            TURN_B: {
                "k": self.canCastle[TURN_B]["k"],
                "q": self.canCastle[TURN_B]["q"],
            },
        }
        new.enPassant = self.enPassant
        new.mateSteps = self.mateSteps
        new.numMoves = self.numMoves
        new.zob_hash_val = self.zob_hash_val
        new.score_val = self.score_val

        return new

    def __repr__(self) -> str:
        pboard = "\n".join([s for s in "".join(self.board).split(EDGE) if s != ""])
        return "-----------\n{}\n{}\n-----------".format(
            pboard, " ".join(self.fen().split(" ")[1::])
        )

    def zobrist_hash(self) -> int:
        if self.zob_hash_val == None:
            ans = 0
            for sq in (21 + i + j * 10 for i in range(8) for j in range(8)):
                ans ^= Z_HASH_BOARD[sq][self.board[sq]]
            ans ^= Z_HASH_TURN[self.turn]
            for turn, side in product((TURN_W, TURN_B), ("k", "q")):
                ans ^= Z_HASH_CASTLE[turn][side][self.canCastle[turn][side]]
            if self.enPassant:
                ans ^= Z_HASH_BOARD[self.enPassant]["e"]
            self.zob_hash_val = ans
        return self.zob_hash_val

    def oldHash(self) -> int:
        return hash(
            (
                "".join(self.board),
                self.turn,
                tuple((tuple(d.values()) for d in self.canCastle.values())),
                self.enPassant,
            )
        )

    def __hash__(self) -> int:
        return self.zobrist_hash() if USE_Z_HASH else self.oldHash()

    def __eq__(self, obj) -> bool:
        return (
            "".join(self.board),
            self.turn,
            tuple((tuple(d.values()) for d in self.canCastle.values())),
            self.enPassant,
        ) == (
            "".join(obj.board),
            obj.turn,
            tuple((tuple(d.values()) for d in obj.canCastle.values())),
            obj.enPassant,
        )

    def fen(self) -> str:
        sboard: str = ""
        for line in "".join(self.board).split(EDGE):
            if line == "":
                continue
            count = 0
            for c in line:
                if c.isalpha():
                    if count != 0:
                        sboard += str(count)
                        count = 0
                    sboard += c
                else:
                    count += 1
            if count != 0:
                sboard += str(count)
            sboard += "/"
        sboard = sboard[: len(sboard) - 1]

        sturn = "w" if self.turn == TURN_W else "b"

        sCastle = ""
        if self.canCastle[TURN_W]["k"]:
            sCastle += "K"
        if self.canCastle[TURN_W]["q"]:
            sCastle += "Q"
        if self.canCastle[TURN_B]["k"]:
            sCastle += "k"
        if self.canCastle[TURN_B]["q"]:
            sCastle += "q"
        if sCastle == "":
            sCastle = "-"

        sEnPassant = ""
        if self.enPassant:
            sEnPassant = sq2alg(self.enPassant)
        else:
            sEnPassant = "-"

        sMatesteps = str(self.mateSteps)
        sNumMoves = str(self.numMoves)

        return " ".join([sboard, sturn, sCastle, sEnPassant, sMatesteps, sNumMoves])

    def isSquareAttacked(self, square: int, turn: bool = None) -> bool:
        if turn == None:
            turn = self.turn

        N, S, W, E = -10, +10, -1, +1
        directions: list = [N, S, W, E, N + W, N + E, S + W, S + E]
        minePieces = PIECES_W if turn == TURN_W else PIECES_B
        hisPieces = PIECES_B if turn == TURN_W else PIECES_W
        front = N if turn == TURN_W else S
        for direction in directions:  # peices apart from Knight
            sq = square
            countSteps = 0
            while True:
                sq += direction
                countSteps += 1
                if self.board[sq] in minePieces + EDGE:
                    break
                if self.board[sq] == "0":
                    continue

                if self.board[sq] in "PKpk":
                    if countSteps > 1:
                        break
                    if self.board[sq] in "Kk":
                        return True
                    else:  # pawn
                        return True if direction in [front + E, front + W] else False
                if self.board[sq] in "BRQbrq":
                    if direction in [N, S, E, W] and self.board[sq] in "RQrq":
                        return True
                    elif (
                        direction in [N + E, N + W, S + E, S + W]
                        and self.board[sq] in "BQbq"
                    ):
                        return True
                    else:
                        break
                break  # Knight
        for direction in [
            N + 2 * W,
            N + 2 * E,
            S + 2 * W,
            S + 2 * E,
            2 * N + W,
            2 * N + E,
            2 * S + W,
            2 * S + E,
        ]:
            sq = square + direction
            if self.board[sq] in hisPieces and self.board[sq] in "Nn":
                return True
        return False

    def isChecked(self, turn: bool) -> bool:
        king = "K" if turn == TURN_W else "k"
        sq = self.board.index(king)
        return self.isSquareAttacked(sq, turn)

    def kingsideKP(self, turn: int = None) -> bool:
        if not turn:
            turn = self.turn
        kingSquare = 95 if turn == TURN_W else 25
        for square in range(kingSquare, kingSquare + 3):
            if self.isSquareAttacked(square, turn):
                return True
        return False

    def queensideKP(self, turn: int = None) -> bool:
        if not turn:
            turn = self.turn
        kingSquare = 95 if turn == TURN_W else 25
        for square in range(kingSquare, kingSquare - 4, -1):
            if self.isSquareAttacked(square, turn):
                return True
        return False

    def isPseudoLeagelMove(self, mv: Move) -> bool:
        return mv in self.allMoves()

    def isLeagalMove(self, mv: Move) -> bool:
        """
        very slow!
        """
        return (mv in self.allMoves()) and (not self.makeMove(mv).isChecked(self.turn))

    @cache
    def mvGen(self) -> list[Move]:
        """
        a list of all pesudo-leagal moves. the king can be checked.
        """
        king = "K" if self.turn == TURN_W else "k"
        if not king in self.board:
            return []

        captures: list[Move] = []
        castles: list[Move] = []
        others: list[Move] = []
        isMine = str.isupper if self.turn == TURN_W else str.islower
        isHis = str.islower if self.turn == TURN_W else str.isupper

        def addAns(fro: int, to: int) -> bool:
            """
            suitable for moves except enpassant and castle.
            return whether to break.
            """
            if self.board[to] == BLANK:
                others.append(Move(fro, to))
                return False
            elif isHis(self.board[to]):
                captures.append(Move(fro, to))
                return True
            return True

        for index, piece in enumerate(self.board):
            if not isMine(piece):
                continue
            if piece in "BRQbrq":
                for direction in DIRS_PIECES[piece]:
                    to = index
                    while True:
                        to += direction
                        if addAns(index, to):
                            break
            elif piece in "NKnk":
                for direction in DIRS_PIECES[piece]:
                    to = index + direction
                    addAns(index, to)
                if piece in "Kk":  # castle
                    # kingside
                    if (
                        self.board[index + E] == self.board[index + 2 * E] == BLANK
                        and self.canCastle[self.turn]["k"] == True
                        and not self.kingsideKP()
                    ):
                        castles.append(Move(index, index + 2 * E))
                    # queenside
                    if (
                        self.board[index + W]
                        == self.board[index + 2 * W]
                        == self.board[index + 3 * W]
                        == BLANK
                        and self.canCastle[self.turn]["q"] == True
                        and not self.queensideKP()
                    ):
                        castles.append(Move(index, index + 2 * W))
            else:  # pawn
                front = N if piece == "P" else S

                to = index + front
                if self.board[to] == BLANK:
                    others.append(Move(index, to))
                for to in [index + front + E, index + front + W]:
                    if isHis(self.board[to]) or to == self.enPassant:
                        others.append(Move(index, to))
                to = index + 2 * front  # the first move
                if (
                    index // 10 == (8 if self.turn == TURN_W else 3)
                    and self.board[to] == BLANK
                    and self.board[index + front] == BLANK
                ):
                    others.append(Move(index, to))
        
        return castles, captures, others

    def allCaptures(self) -> list[Move]:
        return self.mvGen()[1]
    
    def allMoves(self) -> Iterator[Move]:
        return chain.from_iterable(self.mvGen())

    def allLeagalMoves(self) -> list[Move]:
        return [
            mv for mv in self.allMoves() if not self.makeMove(mv).isChecked(self.turn)
        ]

    def makeMove(self, mv: Move):  # -> ChessBot
        """
        this method would assume that this move is leagal.
        """
        pos: Position = self.deepcopy()
        piece2mv = self.board[mv.fro]
        capture = self.board[mv.to]
        pos.board[mv.fro] = BLANK
        pos.board[mv.to] = piece2mv
        pos.zob_hash_val ^= (
            Z_HASH_BOARD[mv.fro][piece2mv]
            ^ Z_HASH_BOARD[mv.to][capture]
            ^ Z_HASH_BOARD[mv.to][piece2mv]
        )
        pos.score_val += (
            -self.sqScore(mv.fro) - self.sqScore(mv.to) + pos.sqScore(mv.to)
        )
        pos.enPassant = None
        if self.enPassant != None:
            pos.zob_hash_val ^= Z_HASH_BOARD[self.enPassant]["e"]
        # enPassant
        isHis = str.islower if self.turn == TURN_W else str.isupper
        if piece2mv in "Pp" and mv.to - mv.fro in {N + N, S + S}:
            for piece in [pos.board[mv.to + E], pos.board[mv.to + W]]:
                if piece in "Pp" and isHis(piece):
                    pos.enPassant = (mv.fro + mv.to) // 2
                    pos.zob_hash_val ^= Z_HASH_BOARD[pos.enPassant]["e"]
        # numMoves
        if pos.turn == TURN_B:
            pos.numMoves += 1
        # 50-steps to draw
        if piece2mv in "Pp" or capture != BLANK:
            pos.mateSteps += 1
        else:
            pos.mateSteps = 0
        # refresh canCastle
        canCastle2refresh: set[tuple[bool, str]] = set()
        # king moved, cannot castle
        if piece2mv in "Kk":
            canCastle2refresh.add((self.turn, "k"))
            canCastle2refresh.add((self.turn, "q"))
        # rook moved, cannot castle
        if piece2mv in "Rr":
            mine_corner_k, mine_corner_q = (91, 98) if self.turn == TURN_W else (21, 28)
            if mv.fro == mine_corner_k:
                canCastle2refresh.add((self.turn, "k"))
            elif mv.fro == mine_corner_q:
                canCastle2refresh.add((self.turn, "q"))
        # rook captured, cannot castle
        if capture in "Rr":
            opposite_corner_q, opposite_corner_k = (
                (21, 28) if self.turn == TURN_W else (91, 98)
            )
            if mv.to == opposite_corner_k:
                canCastle2refresh.add((not self.turn, "k"))
            elif mv.to == opposite_corner_q:
                canCastle2refresh.add((not self.turn, "q"))
        # king captured, cannot castle
        if capture in "Kk":
            canCastle2refresh.add((not self.turn, "k"))
            canCastle2refresh.add((not self.turn, "q"))
        # finally, refreash all canCastle
        for turn, side in canCastle2refresh:
            pos.zob_hash_val ^= Z_HASH_CASTLE[turn][side][self.canCastle[turn][side]]
            pos.canCastle[turn][side] = False
            pos.zob_hash_val ^= Z_HASH_CASTLE[turn][side][False]
        # capture enPassant
        if piece2mv in "Pp" and (mv.to - mv.fro) % N != 0 and capture == BLANK:
            real_capture_sq = mv.to - (N if self.turn else S)
            pos.board[real_capture_sq] = BLANK
            pos.zob_hash_val ^= Z_HASH_BOARD[real_capture_sq][
                self.board[real_capture_sq]
            ]
            pos.score_val -= self.sqScore(real_capture_sq)
        # castle
        if piece2mv in "Kk" and mv.to - mv.fro not in DIRECTIONS:
            # find rook and move it
            try:
                direction = (mv.to - mv.fro) // 2
                for sq in range(mv.to + direction, mv.to + 3 * direction, direction):
                    if pos.board[sq] in "Rr":
                        rook = pos.board[sq]
                        pos.board[sq] = BLANK
                        pos.board[mv.fro + direction] = rook
                        pos.zob_hash_val ^= (
                            Z_HASH_BOARD[sq][rook]
                            ^ Z_HASH_BOARD[mv.fro + direction][rook]
                        )
                        pos.score_val += -self.sqScore(sq) + pos.sqScore(
                            mv.fro + direction
                        )
                        break
            except Exception as e:
                print("rook unbound!")
                print(mv, piece2mv, mv.fro, mv.to)
                print("self:", self)
                print("bot:", pos)
                raise e
        # turn
        pos.turn = not pos.turn
        pos.zob_hash_val ^= Z_HASH_TURN[TURN_B]
        return pos

    def isMiddleGame(self) -> bool:
        return not self.isEndGame

    def isEndGame(self) -> bool:
        count = 0
        for piece in self.board:
            if piece in "BNRQbnrq":
                count += 1
        return count <= 6

    def score(self) -> int:
        if self.score_val == None:
            self.calcScore()
        return self.score_val

    def sqScore(self, sq: int) -> int:
        key = self.board[sq]
        if key == "K":
            key = "KM" if self.isMiddleGame() else "KE"
        elif key == "k":
            key = "km" if self.isMiddleGame() else "ke"
        return PST[key][sq]

    @cache
    def calcScore(self) -> int:
        self.score_val = sum(map(lambda sq: self.sqScore(sq), ITER_BOARD))
        return self.score_val

    @cache
    def gameEnd(self) -> int:
        """
        INF: white wins
        -INF: black wins
        0: no king captured
        """
        white_king = None
        black_king = None
        for sq in ITER_BOARD:
            if self.board[sq] == "K":
                white_king = sq
            elif self.board[sq] == "k":
                black_king = sq
        if not black_king and not white_king:
            raise(Exception("gameEnd(): No king on the board!"))
        elif not black_king:
            return INF
        elif not white_king:
            return -INF
        else:
            return 0

    def move(self, fro, to):
        fro = alg2sq(fro)
        to = alg2sq(to)
        res = self.makeMove(Move(fro, to))
        return res
