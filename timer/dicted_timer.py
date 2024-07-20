d_time: dict[str, float] = dict()


def dicted_timer(func):
    def funcWrapper(*args, **kwargs):
        from time import time

        global d_time

        time_start = time()
        result = func(*args, **kwargs)
        time_end = time()
        time_used = time_end - time_start
        if not func.__name__ in d_time.keys():
            d_time[func.__name__] = [0, 0]
        d_time[func.__name__][0] += 1  # count
        d_time[func.__name__][1] += time_used
        return result

    return funcWrapper
