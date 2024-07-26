import sys
import psutil
import os
import time
import threading

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
    return info.uss / 1024. / 1024.

running = True
memo_by_time = []
def memo_thread():
    while running:
        memo_by_time.append(get_current_memory_mb())
        time.sleep(MEM_TIME_GAP)
        

def test():
    """mem_view = threading.Thread(target=memo_thread)
    mem_view.start()"""
    res = cb.Searcher().go(
        p.Position("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"), TEST_DEPTH
    )
    """running = False
    for i in (range(0, len(memo_by_time), len(memo_by_time) // 10)):
        print(f"{i * MEM_TIME_GAP}s: {memo_by_time[i]}MB")"""
    print(f"mem: {get_current_memory_mb()}MB")
    print("------")
    for key in dt.d_time.keys():
        print(f"{key}: {dt.d_time[key]}")
    return res

if __name__ == "__main__":
    print(f"USE_Z_HASH: {USE_Z_HASH}\nUSE_SELF_CACHE: {USE_SELF_CACHE}\nUSE_AB: {cb.USE_AB}\ndepth: {TEST_DEPTH}\n------")
    print("------\nresult: ", test())
