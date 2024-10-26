from typing import Generator, List, Tuple
import numpy as np


class LedInfo:
    def __init__(self, x: int, y: int, led: int, bit: str, score: int, **kwargs):
        """
        A LedInfo contains 1 or multiple positions where the led is positioned.
        In case of multiple locations, each location gets a verification score.
        The positions with the highest score is considered to be the real location of the led.
        :param x:
        :param y:
        :param led:
        :param bit:
        :param score:
        :param kwargs:
        """
        self._x = [x]
        self._y = [y]
        self.led_id = led  # Address id of the led.
        self.bit = bit  # Binary string used to blink the led
        self._score = np.array(score)  # How close the led Followed the bit pattern in the images. Lower is better.
        self._center_distance = np.array(1)  # How close is the led to the center of the tree
        self._best_match = None
        self._all_coord = []
        self._incorrect = []  # List if indexes of coordinates marked as incorrect
        self.in_string = []  # List of index id of coordinate considered  to be in string.

    def add_location(self, x: int, y: int, score: int, **kwargs):
        self._x.append(x)
        self._y.append(y)
        self._score = np.append(self._score, score)
        self._center_distance = np.append(self._center_distance, 1)
        self._best_match = None
        self._all_coord = []

    @property
    def best_match(self) -> int:
        """
        Calculate the most likely location of the led based on information of all possible led locations in the data.
        :return:
        """
        if len(self.in_string) > 1:
            raise RuntimeError('Only 1 id is expected in self.in_string')
        try:
            return self.in_string[0]
        except IndexError:
            pass

        if not self._best_match:
            if self._score.size == 1:
                self._best_match = 0
            else:
                min = None
                for i in range(len(self._score)):
                    if i not in self._incorrect:
                        if not min or self._score[i] < min:
                            min = self._score[i]

                # scores = self._score/np.max(self._score) * self._center_distance/np.max(self._center_distance)
                if min:
                    self._best_match = np.where(self._score == min)[0][0]
                else:
                    self._best_match = 0
        return self._best_match

    @property
    def active(self):
        """
        A led is active if not all coordinates are marked invalid
        :return:
        """
        return bool(len(self._incorrect) < len(self.all_coord))

    @property
    def x(self):
        return self._x[self.best_match]

    @property
    def y(self):
        return self._y[self.best_match]

    @property
    def coord(self) -> Tuple[int, int]:
        return self.x, self.y

    @property
    def score(self):
        return self._score[self.best_match]

    def calculate_center_distance(self, m, c):
        """
        Calculute the distance for each coordinate to the center
        dist = abs(Y - mX +c)
        :return:
        """
        self._center_distance = np.array([abs(self._y[i] - m * self._x[i] + c) for i in range(len(self._x))])
        self._best_match = None

    def get_alternative_coord(self):
        """
        get a list of x, y tuples matching the secondary optional locations for the Led
        :return:
        """
        return self.all_coord[1:]

    def mark_incorrect(self, coord_id: int):
        if self.led_id == 590:
            print()
        self._incorrect.append(coord_id)
        self._best_match = None

    def coord_id_active(self, coord_id) -> bool:
        """
        Return if coord is still active, or marked as incorrect.
        :param coord_id:
        :return:
        """
        return coord_id not in self._incorrect

    @property
    def all_coord(self) -> List[Tuple[int, int]]:
        """
        :return: List of tuples of all possible coord (x, y)
        """
        if not self._all_coord:
            self._all_coord = [(self._x[idx], self._y[idx]) for idx in range(len(self._x))]
        return self._all_coord

    def get_colored_coord(self) -> Generator[Tuple[Tuple[int, int], str], None, None]:
        for i in range(len(self.all_coord)):
            if i in self._incorrect:
                yield self.all_coord[i], 'purple'
            elif i == self.best_match:
                yield self.all_coord[i], 'green'
            else:
                yield self.all_coord[i], 'red'

    def __str__(self):
        return f"{self.led_id} ({self.x}, {self.y})"
