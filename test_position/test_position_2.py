import position as p
from importlib import reload
from definitions import *

reload(p)

DATAPATH = r"D:\Users\admin\Documents\code\tynerchess\test_position\stockfishResult.txt"


pos = p.Position()
pos.init()


def searchAll(bot: p.Position = pos, depth: int = 0) -> int:
    if depth == 0:
        return 1

    ans = 0
    for mv in bot.allMoves():
        if bot.makeMove(mv).isChecked(bot.turn):
            continue
        n = searchAll(bot.makeMove(mv), depth - 1)
        ans += n
    return ans


def searchByMoves(depth: int) -> dict[p.Move : int]:
    ans = dict()

    global pos
    for mv in pos.allMoves():
        if pos.makeMove(mv).isChecked(pos.turn):
            continue
        ans[mv] = searchAll(pos.makeMove(mv), depth - 1)

    return ans


def readStockfish() -> dict[p.Move : int]:
    ans = dict()
    with open(DATAPATH, "r") as file:
        for line in file:
            smv = line.split(": ")[0]
            num = int(line.split(": ")[1])
            mv = p.Move(p.alg2sq(smv[0:2]), p.alg2sq(smv[2:4]))
            ans[mv] = num
    return ans

@timer
def test(depth):
    myans = searchByMoves(depth)
    sfans = readStockfish()
    print("my\tsf\t")
    for mv in set(myans.keys()) & set(sfans.keys()):
        print(
            "{}\t{}\t{}".format(myans[mv], sfans[mv], mv),
            end="==\n" if myans[mv] == sfans[mv] else "!!\n",
        )
    for mv in set(myans.keys()) - set(sfans.keys()):
        print("{}\t-\t{}".format(myans[mv], mv))
    for mv in set(sfans.keys()) - set(myans.keys()):
        print("-\t{}\t{}".format(sfans[mv], mv))
