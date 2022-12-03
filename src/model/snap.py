import json
from math import radians, sin, pi, sqrt, cos, inf
from statistics import median
from typing import Dict, Optional, List, Tuple

import numpy as np

from pandas import DataFrame
from scipy.signal import argrelmax

from config import IMAGE, LENS_ANGLE
from model.camera import CameraPosition


class SnapLine:
    def __init__(self, x, y, led_id, led_data: 'RawSnapData' = None):
        self.x = x  # x position in snap
        self.y = y  # y position in snap
        self.id = led_id
        self.led_data = led_data
        self.reliable = True

    def distance(self, led: 'SnapLine') -> Optional[float]:
        try:
            return sqrt((self.x - led.x)**2+(self.y - led.y)**2)
        except AttributeError:
            return None

    def next(self, amount=1) -> Optional['SnapLine']:
        """Return led with next id (if exists)
        :param: amount return id + amount as next LedPos
        """
        try:
            return self.led_data.snapl[self.id + amount]
        except KeyError:
            return None

    def previous(self, amount=1) -> Optional['SnapLine']:
        """Return led with previous id (if exists)
        :param: amount return id - amount as previous LedPos
        """
        try:
            return self.led_data.snapl[self.id - amount]
        except KeyError:
            return None

    def average_neighbour_dist(self, amount=1) -> Optional[float]:
        """
        Calculate the average distance to leds in distance amount
        This distance is calculated withing a snap, making the average distance a relative distance in the image.
        The real distance com the camera to the tree is not used for this calcultation
        :param amount: Number of neighbours to inspect on either side of the led
        :return:
        """
        dist = 0
        counter = 0
        for i in range(1, amount + 1):
            if self.next(i):
                dist += self.distance(self.next(i))
                counter += 1
            if self.previous(i):
                dist += self.distance(self.previous(i))
                counter += 1
        if dist > 0:
            return dist / counter
        return None


class RawSnapData:
    """
    RawSnapData data holds all raw information regarding a snap series
    Initially the camera position is estimated based on the raw data.
    This Camera position is later refined based on combining data from multiple snaps.
    RawSnapData will produce data based on the last update of the camera position.
    """
    def __init__(self, data_file):
        self.snapl: Dict[str, SnapLine] = {}
        self.name = data_file.name
        self._median: Optional[float] = None
        self._tree_center: Optional[int] = None
        self._angle_extremes = None

        self.load_data(data_file / 'data.txt')
        self.mark_reliable()

        self.camera_pos = CameraPosition(0, -self.camera_distance(), 0, self.name, self.tree_center, IMAGE[1] / 2)

    def load_data(self, file):
        duplicates = []
        for led in json.loads(file.read_text()):
            if led['led'] == -1:
                continue
            if led['led'] in self.snapl:
                duplicates.append(SnapLine(led['x'], led['y'], led['led'], self))
            else:
                self.snapl[led['led']] = SnapLine(led['x'], led['y'], led['led'], self)

        for led in duplicates:
            if led.average_neighbour_dist() and \
                    led.average_neighbour_dist() < self.snapl[led.id].average_neighbour_dist():
                self.snapl[led.id] = led

    def mark_reliable(self):
        for key, led in self.snapl.items():
            if not led.average_neighbour_dist() or led.average_neighbour_dist() > self.median * 2:
                led.reliable = False

    def improve(self):
        for key in list(self.snapl.keys()):
            if not self.snapl[key].reliable:
                del self.snapl[key]

    @property
    def tree_center(self) -> int:
        """
        Get the pixel in which the tree center is expected.
        This pixel has the lowest mean error when checking distances to active leds. (most in the middle pixel)
        :return:
        """
        if not self._tree_center:
            coord = [led.y for led in self.snapl.values() if led.reliable]
            last_err: Optional[int] = None
            for i in range(min(coord), max(coord)):
                err = 0
                for val in coord:
                    err += (val - i)**2

                if last_err and err > last_err:
                    self._tree_center = i - 1
                    break
                last_err = err

        return self._tree_center

    @property
    def distances(self) -> List[float]:
        data = []
        for led in self.snapl.values():
            if led.next():
                data.append(led.distance(led.next()))
        return data

    @property
    def median(self) -> float:
        if not self._median:
            self._median = median(self.distances)
        return self._median

    @property
    def dataframe(self) -> DataFrame:
        return DataFrame([[0, -self.camera_distance(), 0]])

    def angle_y(self, led: SnapLine) -> float:
        """
        Return angle between the line from the camera to the center of the tree
        :param led:
        :return: angle in radians
        """
        return radians((led.y - self.tree_center) * LENS_ANGLE[0] / IMAGE[0])

    @staticmethod
    def angle_x(led: SnapLine) -> float:
        """
        Return the angle between de line through the led and the center of the image.
        :param led:
        :return:
        """
        return radians(((IMAGE[1] / 2) - led.y) * LENS_ANGLE[1] / IMAGE[1])

    def angle_extremes(self) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        """
        Get the outer angles in de picture (in radians)
        :return: ((x_min, y_min), (x_max, y_max))
        """
        leds = [led for led in self.snapl.values() if led.reliable]
        if not self._angle_extremes:
            self._angle_extremes = ((min([self.angle_y(led) for led in leds]),
                                     min([self.angle_x(led) for led in leds])),
                                    ((max([self.angle_y(led) for led in leds]),
                                      max([self.angle_x(led) for led in leds]))))
        return self._angle_extremes

    def camera_distance(self) -> float:
        """
        Get the camera distance in units. One unit is the expected distance between tree center and most outer led."
        :return:
        """
        angle = max(abs(self.angle_extremes()[0][0]), abs(self.angle_extremes()[1][0]))
        return 1 / sin(angle)

    def angle_fit_data(self, other: 'RawSnapData', num_test_angles=500):
        result = np.ndarray(shape=(num_test_angles, 2), dtype=float)
        for i in range(0, num_test_angles):
            phi = i * 2 * pi / num_test_angles
            result[i] = (phi, 0)

            for led in self.snapl.values():
                if led.reliable and led.id in other.snapl and other.snapl[led.id].reliable:
                    x, y = get_intersection_coord(self, other, phi, led.id)

                    dist = x*x + y*y
                    if dist < 1:
                        result[i, 1] += 1
                    else:
                        result[i, 1] += 1/dist
        return result

    def estimate_angle(self, other: 'RawSnapData') -> Tuple[float, float]:
        data = self.angle_fit_data(other)
        extremes = argrelmax(data, mode='wrap')
        best = (0, 0)
        second = (0, 0)
        for i in extremes[0]:
            x, y = data[i]
            if y > best[1]:
                second = best
                best = (x, y)
            elif y > second[1]:
                second = (x, y)

        return best[0], second[0]

    def all_intersection(self, other: 'RawSnapData', angle, max_dist=2):
        """
        Calculate the coördinates of leds visible by 2 camera's with a given angle between the camera's
        :param other: other LedData camera position
        :param angle: desired angle between the 2 camera's
        :param max_dist: only leds with coordinates smaller than max_dist are added in the returned dict
        :return: Dict. Key is the led id, value is a tuple of x, y, z
        """
        data = {}
        for key in self.snapl.keys():
            if key in other.snapl:
                x, y = get_intersection_coord(self, other, angle, key)
                if -max_dist < x < max_dist and -max_dist < y < max_dist:
                    data[key] = (x, y, 0)
        return data


def get_intersection_coord(cam1: RawSnapData, cam2: RawSnapData, phi, led_id):
    """
    Calculate the intersection coordinate of a led between 2 cameras.
    The returned x, y coordinate is the estimation of where the led is positioned.
    :param cam1: First camera
    :param cam2: Seconds camera
    :param phi: Rotation angle between the camera
    :param led_id: Led to calculate intersection for.
    :return:
    """
    alfa = cam1.angle_y(cam1.snapl[led_id])
    beta = cam2.angle_y(cam2.snapl[led_id])

    a1 = cos(alfa)
    b1 = sin(alfa)
    c1 = - cam1.camera_distance() * sin(alfa)

    a2 = cos(beta - phi)
    b2 = sin(beta - phi)
    c2 = - cam2.camera_distance() * sin(beta)

    try:
        x = ((b1 * c2 - b2 * c1) / (a1 * b2 - a2 * b1))
        y = ((c1 * a2 - c2 * a1) / (a1 * b2 - a2 * b1))
        return x, y
    except ZeroDivisionError:
        return inf, inf
