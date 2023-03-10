from machine import Pin
import neopixel

from config import STRINGS


class Aap:
    pass


class Pixels:
    def __init__(self):
        self.np = []  # Holds all pixels
        self.num_pix_in_string = []  # list of count of pixels in a string
        for sid, data in STRINGS.items():
            self.np.append(neopixel.NeoPixel(Pin(data['pin']), data['numled']))
            self.num_pix_in_string.append(data['numled'])
        self.num_leds = sum(self.num_pix_in_string)
        self.num_strings = len(STRINGS)
        print(f"I have {self.num_leds} Pixels")
        self.disable_led_id = {34: True}

        self.string_change = [False, ] * self.num_strings

    def pixel_loc(self, index) -> tuple[int, int]:
        """
        Get a pixel by a numeric id.
        :return: the matching pixel from 1 of the strings.
        """
        string_id = 0
        for num in self.num_pix_in_string:
            if index - num < 0:
                return string_id, index

            string_id += 1
            index = index - num

    def write(self):
        for i in range(self.num_strings):
            if self.string_change[i]:
                self.np[i].write()
                self.string_change[i] = False

    def show(self):
        self.write()

    def __getitem__(self, index):
        loc = self.pixel_loc(index)
        return self.np[loc[0]][loc[1]]

    def __setitem__(self, index: int, val: tuple[int, int, int]) -> None:
        """
        Set the pixel at *index* to the value, which is an RGB/RGBW tuple.
        """
        if index in self.disable_led_id:
            return
        loc = self.pixel_loc(index)
        if not self.string_change[loc[0]]:
            # Check if value is changed to track changes in pixel strings
            if self.np[loc[0]][loc[1]] != val:
                self.string_change[loc[0]] = True
                self.np[loc[0]][loc[1]] = val
        else:
            self.np[loc[0]][loc[1]] = val

    def __len__(self):
        return self.num_leds


pixels = Pixels()
