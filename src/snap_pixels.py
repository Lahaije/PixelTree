import json
import time
import random
import numpy
from typing import Union
from cv2 import absdiff
from neopixel import NeoPixels, Color
from esp_serial import esp
from webcam import Webcam, read_im, store_im
from config import storage, NUM_PIXELS

np = NeoPixels(NUM_PIXELS)


class Snapper:
    """
    Snapper is used to create all images needed to measure 1 side of the tree.
    Snapper.run() is used to create a series of images.
    First each pixel in the tree is assigned a unique number. This number is translated to a binary number.
    Next for each bit the pixel is turned on in case the bit is high, turned off if the bit is low.
    When making images, first a base image is created with all leds off. The sequence of images representing the bit
    is shot after, and from each image the base image is subtracted to make maximum contrast betwwen led on and led off.
    """
    def __init__(self, series_name: str, snap_color: Union[Color, str] = 'white', num_pixels=NUM_PIXELS):
        self.series_name = series_name
        self.snap_color = snap_color
        self.num_pixels = num_pixels
        (storage / series_name).mkdir(exist_ok=True, parents=True)

    def snap_monochrome(self, name: str, color: Union[Color, str]):
        """
        Create an image in which all the pixels have the same color.
        :param name: Name of the image
        :param color: 1 Color to use for all the pixels in the tree.
        :return:
        """
        for pixel in NeoPixels.pixels:
            pixel.color = color

        esp.write()
        # Hardcoded sleep for now. This sleep could be replaced by some code calculating
        # and waiting the exact time it takes to render the frame.
        time.sleep(0.2)
        store_im(f'{self.series_name}/{name}', Webcam.snap())

    def snap_ground(self):
        """Snap a pixture with all leds off."""
        self.snap_monochrome('ground', 'black')

    def snap_full_on(self):
        """Snap a pixture with all leds on"""
        self.snap_monochrome('all', Color(255, 255, 255))

    def snap_leds(self):
        """Snap N pixtures. In each pixture all leds turn either on or off, depending on their "foto number".
        The foto number is a "random" number each led is assigned.
        With the N pixures, each led will flash a binary pattern.
        This pattern is the binary representation of the foto number of the led.
        :return:
        """
        for n in range(8):
            for pixel in NeoPixels.pixels:
                if pixel.bit_n_set(n):
                    pixel.color = self.snap_color
                else:
                    pixel.color = 'black'
            esp.write()
            time.sleep(0.2)
            store_im(f'{self.series_name}/{n}', Webcam.snap())

    def make_example(self):
        """
        Create an example image showing all snapped foto's in 1 images
        :return:
        """
        ground = read_im(f'{self.series_name}/ground')
        images = [absdiff(read_im(f'{self.series_name}/{n}'), ground) for n in range(8)]

        store_im(f'{self.series_name}/example', numpy.concatenate(
            (numpy.concatenate((images[0], images[1], images[2], images[3]), axis=1),
             numpy.concatenate((images[4], images[5], images[6], images[7]), axis=1)), axis=0))

    def assign_pixel_id(self):
        """
        Assign each pixel a unique random number
        """
        pixel = 0
        id_dict = {}
        for num in random.sample(range(16, 255), self.num_pixels):
            NeoPixels.pixels[pixel].foto_number = num
            id_dict[num] = pixel
            pixel += 1

        with (storage / self.series_name / 'numbers.txt').open('w') as number_file:
            number_file.write(json.dumps(id_dict))

    def run(self):
        """
        Run the sequence needed to measure 1 side of the tree
        """
        self.assign_pixel_id()
        self.snap_ground()
        self.snap_full_on()
        self.snap_leds()
        self.make_example()


if __name__ == "__main__":
    Snapper('testing').run()
