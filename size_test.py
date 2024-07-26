import position as p
import searcher as cb
from definitions import *

from pympler import asizeof

maxDepth = 3
differentPositions: list[set] = []
count: list[int] = []

def asize(obj):
    return asizeof.asizeof(obj)


def dfs(pos: p.Position, depth=maxDepth):
    n = maxDepth - depth
    if n >= len(differentPositions):
        differentPositions.append(set())
        count.append(0)
    differentPositions[n].add(pos)
    count[n] += 1

    if depth == 0:
        return
    for mv in pos.allLeagalMoves():
        dfs(pos.makeMove(mv), depth - 1)
    return


@timer
def timed_dfs(pos, depth):
    dfs(pos, depth)


def main():
    pos = p.Position()
    pos.init()
    global maxDepth
    maxDepth = 4
    timed_dfs(pos, maxDepth)
    print(f"asizeof the set: {asizeof.asizeof(differentPositions)}")
    for i in range(len(differentPositions)):
        print(f"{i}\t{len(differentPositions[i])}\t{count[i]}")


if __name__ == "__main__":
    main()
