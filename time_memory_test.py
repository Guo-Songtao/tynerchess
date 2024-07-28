import sys
import psutil
import os
import time
import cProfile
import random

sys.path.append("..")

import searcher as cb
import position as p
from definitions import *
import timer.dicted_timer as dt

pid = os.getpid()
proc = psutil.Process(pid)


def get_current_memory_mb():
    # 获取当前进程内存占用。
    info = proc.memory_full_info()
    return info.uss / 1024.0 / 1024.0


running = True
memo_by_time = []


def memo_thread():
    while running:
        memo_by_time.append(get_current_memory_mb())
        time.sleep(MEM_TIME_GAP)

@timer
def test_searcher():
    """mem_view = threading.Thread(target=memo_thread)
    mem_view.start()"""
    res = cb.Searcher().go(p.Position().init(TEST_FEN), TEST_DEPTH)
    print(f"mem: {get_current_memory_mb()}MB")
    print("------")
    for key in dt.d_time.keys():
        print(f"{key}: {dt.d_time[key]}")
    return res

@dt.dicted_timer
def new_and_let_index(l: list):
    new = [l[i] for i in range(len(l))]
    return new

@dt.dicted_timer
def new_and_let(l: list):
    new = [p for p in l]
    return new

@dt.dicted_timer
def list_copy(l: list):
    new = l.copy()
    return new

@dt.dicted_timer
def clip(l: list):
    new = l[::]
    return new

@dt.dicted_timer
def new_list(l: list):
    new = list(l)
    return new

@dt.dicted_timer
def list_extend(l: list):
    new = []
    new.extend(l)
    return new


@timer
def test_copy():
    
    for _ in range(100000):
        li = [random.randint(1, 10) for _ in range(120)]
        new = new_and_let_index(li)
        new = new_and_let(li)
        new = list_copy(li)
        new = clip(li)
        new = new_list(li)
        new = list_extend(li)
    print(f"mem: {get_current_memory_mb()}MB")
    print("------")
    for key in dt.d_time.keys():
        print(f"{key}: {dt.d_time[key]}")
    return

def main(depth = TEST_DEPTH):
    print(
        f"USE_Z_HASH: {USE_Z_HASH}\nUSE_SELF_CACHE: {USE_SELF_CACHE}\nUSE_AB: {cb.USE_AB}\ndepth: {depth}\nTEST_FEN: {TEST_FEN}\n------"
    )
    print("------\nresult: ", test_searcher())

if __name__ == "__main__":
    main()