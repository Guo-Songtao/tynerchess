import position as cb
from importlib import reload

reload(cb)

DATAPATH = r"D:\Users\admin\Documents\code\ChessBot-sohu\stockfishResult.txt"


cbot = cb.Position()
cbot.setBegin()


def searchAll(bot: cb.Position = cbot, depth: int = 0) -> int:
    if depth == 0:
        return 1

    ans = 0
    for mv in bot.allMoves():
        if bot.makeMove(mv).isChecked(bot.turn):
            continue
        n = searchAll(bot.makeMove(mv), depth - 1)
        ans += n
    return ans


def searchByMoves(depth: int) -> dict[cb.Move : int]:
    ans = dict()

    global cbot
    for mv in cbot.allMoves():
        if cbot.makeMove(mv).isChecked(cbot.turn):
            continue
        ans[mv] = searchAll(cbot.makeMove(mv), depth - 1)

    return ans


def readStockfish() -> dict[cb.Move : int]:
    ans = dict()
    with open(DATAPATH, "r") as file:
        for line in file:
            smv = line.split(": ")[0]
            num = int(line.split(": ")[1])
            mv = cb.Move(cb.alg2sq(smv[0:2]), cb.alg2sq(smv[2:4]))
            ans[mv] = num
    return ans


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
