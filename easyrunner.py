import position as p
import searcher as s
import time_memory_test as tmt
from definitions import *


def go(fen, depth):
    return s.Searcher().go(p.Position().init(fen), depth)


def clear():
    p.Position.allMoves.cache_clear()
    p.Position.calcScore.cache_clear()


def mem():
    return f"{tmt.get_current_memory_mb()} MB"
