import time, machine, stm

import micropython
import neopixel
import time

print(machine.freq())

np = neopixel.NeoPixel(machine.Pin(4), 8)

np[2] = (255, 111, 111)
np.write()

pp = machine.Pin(4, machine.Pin.OUT)

@micropython.asm_xtensa
def write_zero(r0):
    lsr(r0, r0, 3)
    movwt(r1, stm.GPIOB + stm.GPIO_BSRR)
    mv(r2, 1 << 4)
    label(loop)
    strh(r2, [r1, 0])
    strh(r2, [r1, 2])
    sub(r0, 1)
    bne(loop)



def time_it(f, n):
    tics = time.tics_us
    t0 = tics()
    f(n)
    t1 = tics()
    dt = time.tics_diff(t1, t0)
    print(f'{dt} us')

time_it(write_zero, 10000)
