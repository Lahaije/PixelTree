import json
from typing import List
from numpy import mean

from config import storage


class BitInfo:
    _led_keys = {}  # Translation between real led id and random assigned numbers.

    def __init__(self, data: List, series_name):
        """
        BitInfo takes a list of values a single pixel during a series of led detection images.
        The values are converted to a bit string and number. These can be used to Identify the led the pixel belongs to.
        :param data: list of pixel values
        """
        self.data = data
        self.series_name = series_name
        self._average = 0
        self._bistring = ''
        self._score = 0

    @property
    def average(self) -> float:
        if not self._average:
            self._average = mean(self.data)
        return self._average

    @property
    def bit_string(self) -> str:
        if not self._bistring:
            self._bistring = "".join(['0' if e < self.average else '1' for e in self.data])
        return self._bistring

    @property
    def bit_number(self) -> int:
        return int(self.bit_string, 2)

    @property
    def score(self) -> int:
        if not self._score:
            big = [e for e in self.data if e > self.average]
            small = [e for e in self.data if e < self.average]
            self._score = int(sum((big - mean(big))**2) + sum((small - mean(small))**2))
        return self._score

    @property
    def led_key(self) -> int:
        if not self._led_keys:
            with (storage / self.series_name / 'numbers.txt').open('r') as file:
                self._led_keys = json.loads(file.readline())
        try:
            return self._led_keys[str(self.bit_number)]
        except KeyError:
            return -1
