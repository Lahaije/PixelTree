from random import getrandbits
import gc
import time
import uasyncio as asyncio


def randint(max):
    length = len(f"{max:b}")
    value = getrandbits(length)
    while 0 < value or value > max:
        if value < 0:
            value += getrandbits(length)
        else:
            value -= getrandbits(length)
    return value


async def run_gc(ms=0):
    """
    ms, number of ms this function should delay
    :param ms:
    :return:
    """
    if ms > 0:
        timer = time.ticks_ms()
    gc.collect()
    if ms > 0:
        elapsed = time.ticks_diff(time.ticks_ms(), timer)
        if elapsed - ms > 0:
            await asyncio.sleep(1000/(elapsed - ms))
