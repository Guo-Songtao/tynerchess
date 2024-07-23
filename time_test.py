import sys

sys.path.append("..")

import searcher as cb
import position as p
from definitions import *
import timer.dicted_timer as dt


def test():
    res = cb.Searcher().go(
        p.Position("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"), TEST_DEPTH
    )
    for key in dt.d_time.keys():
        print(f"{key}: {dt.d_time[key]}")
    return res


print(f"USE_CACHE: {USE_CACHE}\nUSE_AB: {cb.USE_AB}\ndepth: {TEST_DEPTH}\n------")
print("------\nresult: ", test())
