# %%
import chess
import chess.pgn as pgn
import datetime
import os
#from itertools import enumerate
from typing import Iterable, Iterator, Tuple

# %%
pgn_path = r"./lichess_db_standard_rated_2024-07.pgn"
def gen_datafile_path():
    return r"./training_data/raw-2024-07--{}.dat".format(str(datetime.datetime.now().strftime("%Y%m%d%H%M%S")))

# %%
def games_iter(path) -> Iterator[Tuple[pgn.GameNode, int]]:
    with open(path, "r") as f:
        count_game = 0
        while (game := pgn.read_game(f)):
            yield game, count_game
            count_game += 1

# %%
def games_with_eval_iter(path) -> Iterator[Tuple[pgn.GameNode, int]]:
    for game, count_game in games_iter(path):
        try:
            if not next(iter(game.mainline())).eval():
                continue
        except Exception:
            continue
        yield game, count_game

# %%
def count_pieces(fen: str):
    res = 0
    for c in fen.split(" ")[0]:
        if c.isalpha():
            res += 1
    return res

def dataset_gen(
        it: Iterator[pgn.Game], num_output_data = 1000, filter = lambda board: True, output_path = None
        ):
    """
    it: iterator of games.
    filter: decide whether this board is to be accepted (True) or not (False).
    """
    if output_path == None:
        output_path = gen_datafile_path()
    os.system(f"cd.>{output_path}")
    with open(output_path, "r+") as out:
        count = 0
        for game, count_game in it:
            if "FEN" in game.headers:
                board = chess.Board(fen = game.headers["FEN"])
            else:
                board = chess.Board()
            for child_node in game.mainline():
                if count > num_output_data:
                    break
                count += 1
                if not filter(child_node):
                    continue
                board.push(child_node.move)
                fen = board.fen()
                eval = child_node.eval().white().score()
                result = {"0-1": -1, "1-0": 1, "1/2-1/2": 0}[child_node.header["Result"]]
                piece_count = count_pieces(fen)
                ply = child_node.ply()
                out.write(f"{fen}\n{eval}\n{result}\n{piece_count}\n{count_game}\n{ply}\n\n")             

# %%
dataset_gen(games_with_eval_iter(pgn_path), 1000)


