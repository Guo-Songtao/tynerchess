from typing import Union, Optional
from copy import deepcopy
from functools import cache

from pst import PST

from definitions import *
import timer.dicted_timer as dt


if not USE_CACHE:

    def cache(func):
        return func


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
    def readFEN(self, fen: str):
        sfen: list[str] = fen.split(" ")

        # board
        for i in range(120):
            self.board[i] = BLANK
        for i in [0, 1, -1, -2]:
            for j in range(10):
                self.board[i * 10 + j] = EDGE
        for i in range(12):
            for j in [0, -1]:
                self.board[i * 10 + j] = EDGE
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

        return self

    @dt.dicted_timer
    def __init__(self, fen: str = None):
        self.board: list[str] = [BLANK] * 120
        self.turn: bool = TURN_W
        self.canCastle: dict[str, dict[str, bool]] = {
            TURN_W: {"k": True, "q": True},
            TURN_B: {"k": True, "q": True},
        }  # canCastle[turn][side_of_board] = True/False
        self.enPassant: Optional[int] = None
        self.mateSteps = 0
        self.numMoves = 1

        if fen:
            self.readFEN(fen)

    @dt.dicted_timer
    def __deepcopy__(self, memo=None):
        new: Position = Position()
        new.board = [self.board[i] for i in range(120)]
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

        return new

    def __repr__(self) -> str:
        pboard = "\n".join([s for s in "".join(self.board).split(EDGE) if s != ""])
        return "-----------\n{}\n{}\n-----------".format(
            pboard, " ".join(self.fen().split(" ")[1::])
        )

    @dt.dicted_timer
    def __hash__(self) -> int:
        """
        containing:
            board(32 dimensions, 64 situations for each)
            turn(1 dimension, 2 situations)
            castle(4 dimensions, 2 situations)
            en passant(1 dimension, 64 situation)
        """
        res = (
            "".join(self.board),
            self.turn,
            tuple(tuple(d.values()) for d in self.canCastle.values()),
            self.enPassant,
        ).__hash__()
        return res

    @dt.dicted_timer
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

    def setBegin(self):
        self.readFEN(FEN_BEGIN)
        return self

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

    @dt.dicted_timer
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

    @dt.dicted_timer
    def isChecked(self, turn: bool) -> bool:
        king = "K" if turn == TURN_W else "k"
        sq = self.board.index(king)
        return self.isSquareAttacked(sq, turn)

    @dt.dicted_timer
    def kingsideKP(self, turn: int = None) -> bool:
        if not turn:
            turn = self.turn
        kingSquare = 95 if turn == TURN_W else 25
        for square in range(kingSquare, kingSquare + 3):
            if self.isSquareAttacked(square, turn):
                return True
        return False

    @dt.dicted_timer
    def queensideKP(self, turn: int = None) -> bool:
        if not turn:
            turn = self.turn
        kingSquare = 95 if turn == TURN_W else 25
        for square in range(kingSquare, kingSquare - 4, -1):
            if self.isSquareAttacked(square, turn):
                return True
        return False

    @dt.dicted_timer
    def isPseudoLeagelMove(self, mv: Move) -> bool:
        return mv in self.allMoves()

    @dt.dicted_timer
    def isLeagalMove(self, mv: Move) -> bool:
        """
        very slow!
        """
        return (mv in self.allMoves()) and (not self.makeMove(mv).isChecked(self.turn))

    @dt.dicted_timer
    def allMoves(self) -> tuple[Move, ...]:
        """
        a list of all pesudo-leagal moves. the king can be checked.
        """
        ans = []
        isMine = str.isupper if self.turn == TURN_W else str.islower
        isHis = str.islower if self.turn == TURN_W else str.isupper

        for index, piece in enumerate(self.board):
            if not isMine(piece):
                continue
            if piece in "BRQbrq":
                for direction in DIRS_PIECES[piece]:
                    to = index
                    while True:
                        to += direction
                        if self.board[to] == BLANK:
                            ans.append((index, to))
                        elif isHis(self.board[to]):
                            ans.append((index, to))
                            break
                        else:
                            break
            elif piece in "NKnk":
                for direction in DIRS_PIECES[piece]:
                    to = index + direction
                    if self.board[to] == BLANK:
                        ans.append((index, to))
                    elif isHis(self.board[to]):
                        ans.append((index, to))
                if piece in "Kk":  # castle
                    # kingside
                    if (
                        self.board[index + E] == self.board[index + 2 * E] == BLANK
                        and self.canCastle[self.turn]["k"] == True
                        and not self.kingsideKP()
                    ):
                        ans.append((index, index + 2 * E))
                    # queenside
                    if (
                        self.board[index + W]
                        == self.board[index + 2 * W]
                        == self.board[index + 3 * W]
                        == BLANK
                        and self.canCastle[self.turn]["q"] == True
                        and not self.queensideKP()
                    ):
                        ans.append((index, index + 2 * W))
            else:  # pawn
                front = N if piece == "P" else S

                to = index + front
                if self.board[to] == BLANK:
                    ans.append((index, to))
                for to in [index + front + E, index + front + W]:
                    if isHis(self.board[to]) or to == self.enPassant:
                        ans.append((index, to))
                to = index + 2 * front  # the first move
                if (
                    index // 10 == (8 if self.turn == TURN_W else 3)
                    and self.board[to] == BLANK
                    and self.board[index + front] == BLANK
                ):
                    ans.append((index, to))
        ans = tuple((Move(*mv) for mv in ans))
        return ans

    @cache
    @dt.dicted_timer
    def allLeagalMoves(self) -> tuple[Move, ...]:
        return tuple(
            (mv for mv in self.allMoves() if not self.makeMove(mv).isChecked(self.turn))
        )

    @dt.dicted_timer
    def makeMove(self, mv: Move):  # -> ChessBot
        """
        this method would assume that this move is leagal.
        """
        bot: Position = deepcopy(self)
        piece = bot.board[mv.fro]
        capture = bot.board[mv.to]
        bot.board[mv.fro] = BLANK
        bot.board[mv.to] = piece
        bot.enPassant = None
        # enPassant
        isHis = str.islower if self.turn == TURN_W else str.isupper
        if piece in "Pp" and mv.to - mv.fro in {N + N, S + S}:
            for piece in [bot.board[mv.to + E], bot.board[mv.to + W]]:
                if piece in "Pp" and isHis(piece):
                    bot.enPassant = (mv.fro + mv.to) // 2
        if bot.turn == TURN_B:
            bot.numMoves += 1
        # 50-steps to draw
        if piece in "Pp" or capture != BLANK:
            bot.mateSteps += 1
        else:
            bot.mateSteps = 0
        # king moved, cannot castle
        if piece in "Kk":
            bot.canCastle[bot.turn]["k"] = bot.canCastle[bot.turn]["q"] = False
        # rook moved, cannot castle
        if mv.fro in [21, 91]:
            bot.canCastle[bot.turn]["q"] = False
        elif mv.fro in [28, 98]:
            bot.canCastle[bot.turn]["k"] = False
        # rook captured, cannot castle
        if mv.to in [21, 91] and capture in "Rr":
            bot.canCastle[not bot.turn]["q"] = False
        elif mv.to in [28, 98] and capture in "Rr":
            bot.canCastle[not bot.turn]["k"] = False
        # capture enPassant
        if piece in "Pp" and (mv.to - mv.fro) % N != 0 and bot.board[mv.to] == BLANK:
            front = N if bot.turn else S
            bot.board[mv.to - front] = BLANK
        # castle
        if piece in "Kk" and mv.to - mv.fro not in DIRECTIONS:
            # find rook and move it
            direction = (mv.to - mv.fro) // 2
            for sq in range(mv.to + direction, mv.to + 3 * direction, direction):
                if bot.board[sq] in "Rr":
                    rook = bot.board[sq]
                    bot.board[sq] = BLANK
            bot.board[mv.fro + direction] = rook
        # turn
        bot.turn = not bot.turn
        return bot

    @dt.dicted_timer
    def checkmate(self) -> bool:
        """
        True: the side to move is checked and has no leagal move.
        False: still have leagal move(s).
        """
        return len(self.allLeagalMoves()) == 0 and self.isChecked(self.turn)

    @dt.dicted_timer
    def gameEnd(self) -> Optional[int]:
        """
        Checkmate: -> INF or -INF
            no leagal moves while king attacked
        Draw: -> 0
            1. no leagal moves while no king attacked
            2. no enough pieces
                1)no pawns;
                2)no rooks, queens;
                3)no more than 2 light pieces
        Game going on: -> None
        """
        if len(self.allLeagalMoves()) == 0:
            if self.isChecked(self.turn):
                return -INF if self.turn == TURN_W else INF
            return 0

        countPieces: dict = {piece: 0 for piece in PIECES + BLANK + EDGE}
        for piece in self.board:
            countPieces[piece] += 1
        if (
            countPieces["P"]
            == countPieces["p"]
            == countPieces["R"]
            == countPieces["r"]
            == countPieces["Q"]
            == countPieces["q"]
            == 0
            and countPieces["N"]
            + countPieces["n"]
            + countPieces["B"]
            + countPieces["b"]
            <= 2
        ):
            return 0

        return None

    @dt.dicted_timer
    def isMiddleGame(self) -> bool:
        return not self.isEndGame

    @dt.dicted_timer
    def isEndGame(self) -> bool:
        count = 0
        for piece in self.board:
            if piece in "BNRQbnrq":
                count += 1
        return count <= 6

    @dt.dicted_timer
    @cache
    def calcScore(self) -> int:
        if self.gameEnd() != None:
            return self.gameEnd()

        res = 0
        for i in range(120):
            key = self.board[i]
            if key == "K":
                key = "KM" if self.isMiddleGame() else "KE"
            elif key == "k":
                key = "km" if self.isMiddleGame() else "ke"
            res += PST[key][i]

        return res

    def move(self, fro, to):
        fro = alg2sq(fro)
        to = alg2sq(to)
        res = self.makeMove(Move(fro, to))
        return res
