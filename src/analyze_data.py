import json
from functools import cached_property
from math import sqrt
import numpy as np
from typing import Dict, Generator, List, Optional, Tuple, Union

from config import storage, NUM_PIXELS
from cv2plot import DataPlot
from model.led_info import LedInfo

"""
This is an copy of analyze data.
This file will rework how strings are stored.
"""

def distance(c1: Tuple[int, int], c2: Tuple[int, int]) -> float:
    """
    calculate distance between 2 points
    :param c1:
    :param c2:
    :return:
    """
    return sqrt((c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2)


def least_squares_fit(x: list, y: list) -> Tuple[float, float]:
    x = np.array(x)
    y = np.array(y)

    array = np.vstack([x, np.ones(len(x))]).T
    (m, c) = np.linalg.lstsq(array, y, rcond=None)[0]

    """
    res = np.polyfit(x, y, 1)
    m = res[0]
    c = res[1]
    """
    return m, c


def dist_point_to_line(x, y, m, c):
    return abs(m*x - y + c) / sqrt(m**2 + 1)


class LedString:
    def __init__(self, leds: List[LedInfo] = None):
        """
        A LedString is a string of leds, detected in an image, with all leds more ore less on a strait line.
        The estimated line can be reconstructed using Y = mx + c
        Leds on a line have increasing ID, but not all led ID are included in a consecutive series.
        If more than X consecutive Id's are missing, the series is ended and a new String is started.
        :param
        """
        self.m: Optional[float] = None
        self.c: Optional[float] = None
        self.coord: List[Tuple[int, int]] = []
        self.leds = leds

    def fill_coord(self):
        self.coord = [led.coord for led in self.leds]


class Estimation:
    def __init__(self):
        """
        Estimation can be used after the HEIGHT of the leds in the tree is estimated in file height.py
        Estimation will take the global height estimation of all leds, and project the global height in the local snap.
        This can be used to scale the leds in a snap, independent of the camera distance.
        """

        # The top_led_x and the bot_led_x are x coördinate of the highest and lowest led in the Container.
        self.top_led_x: Optional[int] = 0
        self.bot_led_x: Optional[int] = 0

        # The Max and min height are the scaled ( 0 to 1 ) height positions of the top and bot led.
        self.max_height: Optional[float] = 0  # Real heights in the tree
        self.min_height: Optional[float] = 1

        # Very rough estimate for camera distance available in 2024_10_13.py
        # Function is called estimate_distance
        self.camera_distance: Optional[float] = None

    def scaled_led_height(self, led: LedInfo) -> float:
        return (self.bot_led_x - led.x) * self.pixelscale + self.min_height

    @cached_property
    def pixelscale(self) -> float:
        """
        pixelscale is a rough estimation to assign a distance to a pixel. it is based on the estimated tree height.
        X and Y are scaled the same, although the camera lens is not equal in these distances.
        """
        return (self.max_height - self.min_height)/(self.bot_led_x - self.top_led_x)


class DataContainer:
    def __init__(self, snap_name):
        self.snap_name = snap_name
        self.data: Dict[int, LedInfo] = {}

        self._m = None
        self._c = None

        self.led_strings: List[LedString] = []
        self.estimate = Estimation()

        self.load_data()
        self.find_strings()

    def load_data(self):
        with (storage / self.snap_name / 'data.txt') as file:
            for row in json.loads(file.read_text()):
                try:
                    self.data[row['led']].add_location(**row)
                except KeyError:
                    self.data[row['led']] = LedInfo(**row)

    @property
    def m(self):
        """
        Y = mx + c
        m coefficient of above line formula
        :return:
        """
        if not self._m:
            self.center_line()
        return self._m

    @property
    def c(self):
        """
        Y = mx + c
        m coefficient of above line formula
        :return:
        """
        if not self._c:
            self.center_line()
        return self._c

    def center_line(self):
        x, y = self.vectorize_led_coord(list(self.data.keys()))
        (self._m, self._c) = least_squares_fit(x, y)

    def vectorize_led_coord(self, id_list: List[int]) -> Tuple[List[int], List[int]]:
        """
        For a list of given led id, repack x and y coordinate in an X vector and an Y vector.
        :param id_list: list of led id
        :return:
        """
        x = [self.data[i].x for i in id_list]
        y = [self.data[i].y for i in id_list]
        return x, y

    def calc_led_center_distance(self):
        for led in self.data.values():
            led.calculate_center_distance(self.m, self.c)
        self._m = None

    def find_strings(self, max_gap=4):
        """
        Find ledstrings of consecutive detected leds.
        A string is considered complete if max_gap consecutive leds are not present.
        """
        start = True
        strings: List[List[LedInfo]] = []
        self.led_strings = []  # Empty led strings to add set of strings which are all active.

        for i in range(NUM_PIXELS):
            try:
                led = self.data[i]
            except KeyError:
                continue
            if led.active:
                if start:
                    strings.append([led])
                    start = False
                elif i - strings[-1][-1].led_id <= max_gap:
                    strings[-1].append(led)
                else:
                    strings.append([led])

        for led_string in strings:
            if len(led_string) > 1:
                self.led_strings.append(LedString(led_string))
        return strings

    def sort_leds_by_height(self):
        return sorted(self.data.values(), key=lambda led: led.x)


def get_new_plot(snap_name: str, scale: int, holding: DataContainer) -> DataPlot:
    plot = DataPlot(snap_name)
    plot.rescale(scale)

    plot.line_mx_c(holding.m, holding.c, 'blue')

    return plot


def plot_leds_colored(plot: DataPlot, holding: DataContainer):
    for led_id, led in holding.data.items():
        for entry in led.get_colored_coord():
            coord = entry[0]
            if entry[1] != 'green':
                continue
            plot.plot_led(coord[0], coord[1], entry[1], led_id)


def extract_most_likely_leds(holding: DataContainer):
    for led_id, led in holding.data.items():
        print(led)


def all_coord_options(leds: List[LedInfo]) -> Generator[List[Tuple[LedInfo, int]], None, None]:
    """
    Generate a table with unique rows.
    Each row contains a list of all leds. Each led is combined with an index.
    The index is the index of a potential coord of the led.
    The full table contains all possible combinations for the provided LedInfo List.
    """
    for i in range(len(leds[0].all_coord)):
        if not leds[0].coord_id_active(i):
            continue
        if len(leds) == 1:
            yield [(leds[0], i)]
            continue
        for entry in all_coord_options(leds[1:]):
            yield [(leds[0], i)] + entry


def get_neighbour_distance(coord: List[Tuple[int, int]]) -> List[float]:
    """
    Calculate the average distance to the neighbouring coord.
    For the edge, the distance of only 1 neighbour is used for the average.
    :param coord: List of coordinates
    :return: List of average distances
    """
    dist = []
    for i in range(len(coord)):
        if i == 0:
            dist.append(distance(coord[i], coord[i+1]))
        elif i == len(coord)-1:
            dist.append(distance(coord[i-1], coord[i]))
        else:
            dist.append((distance(coord[i - 1], coord[i])+ distance(coord[i], coord[i+1]))/2)
    return dist


def optimize_led_strings(holding: DataContainer) -> None:
    holding.find_strings()  # Find strings with active leds
    disabled = False

    for string in holding.led_strings:
        best: List[Tuple[LedInfo, int]] = []
        score = None

        for row in all_coord_options(string.leds):
            string_coord = [entry[0].all_coord[entry[1]] for entry in row]

            x = [c[0] for c in string_coord]
            y = [c[1] for c in string_coord]

            m, c = least_squares_fit(x, y)

            """
            Calculate the error for the fitted line through the option.
            """
            err = 0
            for p in string_coord:
                err = err + dist_point_to_line(p[0], p[1], m, c)**2

            dist = 0
            for i in range(len(string_coord) - 1):
                dist += distance(string_coord[i], string_coord[i+1])

            err = err * dist
            if not score or err < score:
                score = err
                best = row
                string.m = m
                string.c = c
                string.coord = string_coord

        distances = np.array(get_neighbour_distance(string.coord))

        if np.max(distances) > 2 * np.average(distances):
            a = np.where(distances == np.max(distances))[0][0]
            best[a][0].mark_incorrect(best[a][1])
            disabled = True
        else:
            for led, index in best:
                if index not in led.in_string:
                    led.in_string.append(index)

    if disabled:
        """
        Strings led to disabled leds. Rerun
        """
        return optimize_led_strings(holding)


def export_led_positions(snap_name:str, data):
    with (storage / snap_name / 'led_export.json') as file:
        file.write_text(json.dumps(data))


def show_data(snap_name: str, scale, store=False):
    """
    :param snap_name: Name of the snap folder
    :param scale: scale
    :param store: If false, plot shows in window. If True, image is stored in snap folder.
    :return:
    """
    holding = DataContainer(snap_name)
    holding.calc_led_center_distance()

    plot = get_new_plot(snap_name, scale, holding)

    """
    for string in holding.led_strings:
        string.fill_coord()
        for i in range(len(string.coord) - 1):
            plot.draw_line(string.coord[i], string.coord[i + 1], 'red')
    """

    optimize_led_strings(holding)

    for string in holding.led_strings:
        for i in range(len(string.coord) - 1):
            plot.draw_line(string.coord[i], string.coord[i + 1], 'yellow')

        # plot.line_mx_c(string['m'], string['c'], 'red')

    plot_leds_colored(plot, holding)

    if store:
        plot.store('show_data')
    else:
        plot.show()

    data = {'m': holding.m, 'c': holding.c}
    for led in holding.data:
        data[led] = holding.data[led].coord

    export_led_positions(snap_name, data)


if __name__ == "__main__":
    show_data('Monkey', 2, False)

    exit()
    for folder in storage.glob('*'):
        if 'backup' not in folder.parts:
            try:
                (folder / 'show_data_0.png').unlink()
                (folder / 'show_data_1.png').unlink()
            except Exception:
                pass
            show_data(folder.name, 5, True)

    for folder in storage.glob('*/analyze_*'):
        if 'backup' not in folder.parts:
            show_data(folder.name, 5, True)
