from typing import List, Union, Optional
from communication.wifi import Frame, pixelTree


class Color:
    """
    This is a helper class to easily alter the colors of the neopixels.
    This class can be extended in the future by a main dimmer, difference color spaces, etc.
    Some predefined colors are present to easily test.
    """
    predefined = {
        'red': (200, 0, 0),
        'green': (0, 200, 0),
        'blue': (0, 0, 200),
        'white': (150, 150, 150),
        'black': (0, 0, 0),
        'off': (0, 0, 0),
        'purple': (200, 0, 200)
    }

    def __init__(self, r: int = 0, g: int = 0, b: int = 0):
        self.red = r
        self.green = g
        self.blue = b

    def __str__(self):
        return f"( {self.red} , {self.green} , {self.blue} )"


class Pixel:
    """
    A pixel has a 1 to 1 relation with a physical led in the tree.
    The pixel holds the desired color of the led in the tree before for the next frame.
    The id of the pixel is the position of the led in the tree. (pixel 1 is the 1st led, pixel 2, the 2nd etc.

    The foto_number is a unique ID for the pixels used to find the position in a snapped picture.
    The foto_number of led N and N+1 should greatly differ to make sure both leds have a completely different
    pattern when detecting the position of the led in a snapped picture.
    The foto_number is converted to a binary pattern determining in which foto a led is on or off.

    The color can either be set as one of the pre-defined string colors, or a Color object.
    """
    def __init__(self, r: int = 0, g: int = 0, b: int = 0):
        self._color = Color(r, g, b)
        self.id = len(NeoPixels.pixels)
        self.foto_number: Optional[int] = None  # Unique id used in flash cycle when auto-detecting location with webcam
        NeoPixels.pixels.append(self)

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, c: Union[Color, str]):
        if isinstance(c, Color):
            self._color = c
            return
        try:
            self._color = Color(*Color.predefined[c])
        except KeyError:
            raise RuntimeError(f'Invalid color requested "{c}"')

    def json(self):
        return {'r': self.color.red,
                'g': self.color.green,
                'b': self.color.blue}

    def bit_n_set(self, n):
        return self.foto_number >> n & 1


class NeoPixels:
    """NeoPixels holds all the pixels present in the tree"""
    pixels: List[Pixel] = []

    def __init__(self, num: int):
        if self.pixels:
            raise RuntimeError('Pixels already initialized')

        for i in range(num):
            Pixel(0, 0, 0)

    @staticmethod
    def json():
        return{"rgb": [p.json() for p in NeoPixels.pixels]}

    @staticmethod
    def send_by_wifi():
        f = Frame()
        for i in range(len(NeoPixels.pixels)):
            col = NeoPixels.pixels[i].color
            f.leds[i] = [col.red, col.green, col.blue]
        pixelTree.send_frame(f, False)
