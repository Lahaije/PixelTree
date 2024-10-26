import uasyncio
import time
from util import randint
from hue import col, RGB
from pixel import pixels
from frame import frames

CURR_PROG = 'strait'
SPEED = 350


class ProgCol:
    """
    Class to generate colors
    """
    color_list = ['blue', 'green', 'purple', 'sky_blue', 'yellow']  # List of Color for the program
    color_index = 0

    mode = 'next'  # Next or Random

    @staticmethod
    def next():
        """
        Get the next color
        :return:
        """
        if ProgCol.mode == 'next':
            ProgCol.color_index += 1
            if ProgCol.color_index >= len(ProgCol.color_list):
                ProgCol.color_index = 0

            return col(ProgCol.color_list[ProgCol.color_index])

        return col(ProgCol.color_list[randint(len(ProgCol.color_list))])


current_col_num = 0


async def strait():
    color = ProgCol.next()
    for i in range(len(pixels)):
        await uasyncio.sleep_ms(SPEED)
        if CURR_PROG != 'strait':
            break
        pixels[i] = color
        pixels.show()


async def switch_reverse():
    color = ProgCol.next()
    mx = len(pixels)
    for i in range(mx):
        await uasyncio.sleep_ms(SPEED)
        if CURR_PROG != 'reverse':
            break
        pixels[mx - i - 1] = color
        pixels.show()


def step_color(org, desired):
    a, b, c = desired
    x, y, z = org
    change = False
    if x < a:
        x += 1
        change = True
    if x > a:
        x -= 1
        change = True
    if y < b:
        y += 1
        change = True
    if y > b:
        y -= 1
        change = True
    if z < c:
        z += 1
        change = True
    if z > c:
        z -= 1
        change = True

    return change, (x, y, z)


async def fade():
    desired = ProgCol.next()
    print(f"Fading to {desired}")

    while CURR_PROG == 'fade':
        all_correct = True
        for i in range(len(pixels)):
            if i in pixels.disable_led_id:
                continue
            data = step_color(pixels[i], desired)

            if data[0]:

                all_correct = False
                pixels[i] = data[1]
        if all_correct:
            break
        pixels.show()
        await uasyncio.sleep_ms(SPEED)


def twinkle_colors(steps):
    """
    Twinkle between 2 colors
    :param steps:
    :return:
    """
    a = ProgCol.next()
    b = ProgCol.next()
    if len(ProgCol.color_list) > 1:
        while a == b:
            b = ProgCol.next()
    return twinkle_array(a, b, steps)


def twinkle_col_black(steps):
    """
    Twinkle between a color and black
    :param steps:
    :return:
    """
    a = (0,0,0)
    b = ProgCol.next()
    while a == b:
        b = ProgCol.next()
    return twinkle_array(a, b, steps)



def twinkle_array(col_a, col_b, steps):
    """
    Make a list of colors stepping in steps from color A to color B and back.
    :param col_a: color
    :param col_b: color
    :param steps: amount of steps taking to switch color.
    :return:
    """
    dx = int((col_a[0] - col_b[0]) / steps)
    dy = int((col_a[1] - col_b[1]) / steps)
    dz = int((col_a[2] - col_b[2]) / steps)

    res = [col_a]
    for step in range(1, steps):
        res.append((col_a[0] - dx * step, col_a[1] - dy * step, col_a[2] - dz * step))
    res.append(col_b)
    for step in range(1, steps):
        res.append((col_b[0] + dx * step, col_b[1] + dy * step, col_b[2] + dz * step))

    return res


async def run_twinkle(program, steps, color_func):
    """
    run tinkle program
    :param program: name of program
    :param steps: num steps
    :param color_func: function to get new colors
    """
    col = color_func(steps)
    start = -1
    while CURR_PROG == program:
        start += 1
        print(start)
        if start == 2*steps:
            start = 0
            col = color_func(steps)

        j = start
        for i in range(len(pixels)):
            j += 1
            if j == 2*steps:
                j = 0
            pixels[i] = col[j]
        pixels.show()
        await uasyncio.sleep_ms(SPEED)


async def twinkle_black():
    await run_twinkle('twinkle_black', 4, twinkle_col_black)


async def twinkle():
    steps = 4
    col = twinkle_colors(steps)
    start = -1
    while CURR_PROG == 'twinkle':
        start += 1
        print(start)
        if start == 2*steps:
            start = 0
            col = twinkle_colors(steps)

        j = start
        for i in range(len(pixels)):
            j += 1
            if j == 2*steps:
                j = 0
            pixels[i] = col[j]
        pixels.show()

        await uasyncio.sleep_ms(SPEED)


async def run_frame():
    start = time.ticks_ms()
    if frames.run_next():
        expired = time.ticks_diff(time.ticks_ms(), start)
        frame_time = int(1000 / frames.fps)
        if expired < frame_time:
            print(f"Frame sleep {frame_time - expired} ms")
            await uasyncio.sleep_ms(frame_time - expired)
    else:
        await uasyncio.sleep_ms(1)

programs = {
    'strait': strait,
    'reverse': switch_reverse,
    'fade': fade,
    'twinkle': twinkle,
    'twinkle_black': twinkle_black,
    'run_frame': run_frame
}


async def run():
    while True:
        if CURR_PROG == 'direct':
            await uasyncio.sleep_ms(10000)
            continue

        await programs[CURR_PROG]()
