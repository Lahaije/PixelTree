RGB = (0, 0, 0)

class Color:
    black = (0, 0, 0)
    blue = (0, 0, 200)
    green = (200, 0, 0)
    purple = (0, 180, 30)
    red = (0, 200, 0)
    white_ice = (72, 72, 72)
    yellow = (85, 120, 0)
    white_warm = (100, 139, 20)
    sky_blue = (125, 0, 125)


def col(color: str):
    if color == 'rgb':
        return RGB
    return getattr(Color, color)


def col_list():
    for color in Color.__dict__:
        if color[0] == '_':
            continue
        yield color


def set_rgb(r, g, b):
    global RGB

    if r < 0:
        r = 0
    if g < 0:
        g = 0
    if b < 0:
        b = 0
    if r > 255:
        r = 255
    if g > 255:
        g = 255
    if b > 255:
        b = 255
    RGB = (g, r, b)