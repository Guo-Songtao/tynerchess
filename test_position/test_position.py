import position as p
from importlib import reload

reload(p)

DATAPATH = r"D:\Users\admin\Documents\code\ChessBot-sohu\stockfishResult.txt"


bot = None


def testByNumsOfSituations_dfs(bot: p.Position, depth: int = 1):
    if depth == 0:
        return 1

    ans = 0
    moves = bot.allMoves()
    for mv in moves:
        if bot.isLeagalMove(mv):
            ans += testByNumsOfSituations_dfs(bot.makeMove(mv), depth - 1)

    return ans


def testDevidingMoves(bot: p.Position, depth: int):
    count = 0
    res = []
    moves = bot.allMoves()
    for mv in moves:
        if not bot.isLeagalMove(mv):
            continue
        i = testByNumsOfSituations_dfs(bot.makeMove(mv), depth - 1)
        print("after {}: {}".format(mv, i))
        count += i
        res.append([mv, i])
    return res, count


def init():
    global bot
    bot = p.Position()
    bot.init()


def testdiv(boter=bot):
    res, count = testDevidingMoves(boter, depth=4)
    sfRes = []
    sfCount = 0
    with open(DATAPATH, "r") as file:
        for line in file:
            s = line.split(": ")
            smv = s[0]
            i = int(s[1])
            sfCount += int(i)
            mv = p.Move(p.alg2sq(smv[0:2]), p.alg2sq(smv[2::]))
            sfRes.append((mv, int(i)))


if __name__ == "__main__":
    print("""----------------\ntest_chessbot:\ndepth result""")
    for depth in range(5):
        bot = p.Position()
        bot.init()
        print(testDevidingMoves(5))
