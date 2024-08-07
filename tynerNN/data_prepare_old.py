from definitions import *
import position as p

import re
from typing import Iterable, Iterator


f = open("lichess_db_standard_rated_2024-07.pgn", "r")


class Data:
    def __init__(self, fen, score):
        self.fen = fen
        self.score = score
    
    def __repr__(self):
        return f"Data[{self.score}, {self.fen}]"

    def store_form(self):
        return f"{self.score}\t{self.fen}"

class Game:
    def __init__(self):
        self.seqMvs: list[tuple[p.Move, int]] = []
        self.result: int = None # 1/0/-1
        self.elo: int = 0

        self.mvpat = re.compile(r"([A-Z]*)([a-z]+)([0-9])")

    def setResult(self, res: str):
        match res:
            case "1-0": self.result = 1
            case "0-1": self.result = -1
            case "1/2-1/2": self.result = 0

    def __repr__(self) -> str:
        return f"Game[result: {self.result}, elo: {self.elo}, seqMvs: {self.seqMvs}]"
    
    def __iter__(self, no_Repeat = False) -> Iterator[Data]:
        pos = p.Position()
        pos.init()
        for mv, score in self.seqMvs:
            mvmatch: re.Match = self.mvpat.match()
            piece = mvmatch.group(1)
            if not piece:
                piece = "P"
            to_square = p.alg2sq(mvmatch.group(2))
            for leagal_mv in pos.allLeagalMoves():
                if leagal_mv.to == to_square and pos.board[leagal_mv.fro] in (piece, piece.lower()):
                    pass
                    

    

class GameReader:
    def __init__(self, datafile):
        self.f = datafile
        self.valpat: re.Pattern = re.compile(r'\[(.*?) "(.*?)"\]') # e.g. [Result "0-1"]
        self.pgnpat: re.Pattern = re.compile(r"([a-h][1-8]) \{ \[%eval (.*?)\].*?}")

    def __iter__(self):
        game = Game()
        elo = 0
        for line in self.f:
            if len(line) == 1:
                continue
            m = self.valpat.match(line)
            if m: #match
                match m.group(1):
                    case "Result":
                        game.setResult(m.group(2))
                    case "WhiteElo":
                        elo = int(m.group(2))
                    case "BlackElo":
                        game.elo = (elo + int(m.group(2))) // 2
                    case _:
                        pass
                continue
            else: # not match, this line is game record.
                gameseq = self.pgnpat.findall(line)
                if len(gameseq) == 0:
                    game = Game()
                    elo = 0
                    continue
                pos = p.Position()
                pos.init()
                for mv, score in gameseq:
                    if score[0] == "#":
                        if score[1] == "-":
                            score = -INF
                        else:
                            score = INF
                    else:
                        score = int(100 * float(score))
                    game.seqMvs.append((mv, score))
                yield game
                #finally
                game = Game()
                elo = 0
                continue
