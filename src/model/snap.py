import json
from math import radians, sin, sqrt
from statistics import median
from typing import Dict, Optional, List, Tuple

from pandas import DataFrame

from config import IMAGE, LENS_ANGLE
from model.camera import CameraPosition
from model.positions import pixel_positions
from model.transformations import rotate_xy, rotate_pixel_dict


class SnapLine:
    """
    A snap line represents a line from the camera through the neopixel.
    """
    def __init__(self, x, y, led_id, led_data: 'RawSnapData' = None):
        self.x = x  # x position in snap
        self.y = y  # y position in snap
        self.id = led_id
        self.led_data = led_data
        self.reliable = True

    def distance(self, led: 'SnapLine') -> Optional[float]:
        """
        Relative distance between 2 neopixels.
        :param led: Line to other neopixel
        :return:
        """
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

    def camera_distance(self):
        if not self.id in pixel_positions.latest():
            raise LookupError(f'No estimated position for led {self.id} available')



class RawSnapData:
    """
    RawSnapData data holds all raw information regarding a snap series
    Initially the camera position is estimated based on the raw data.
    This Camera position is later refined based on combining data from multiple snaps.
    RawSnapData will produce data based on the last update of the camera position.
    """
    def __init__(self, data_file):
        self.snapl: Dict[int, SnapLine] = {}
        self.name = data_file.name
        self._median: Optional[float] = None
        self._tree_center: Optional[int] = None
        self._angle_extremes = None

        self.load_data(data_file / 'data.txt')
        self.mark_reliable()

        self.camera_pos = CameraPosition(self.camera_distance_estimation(), 0, 0,
                                         self.name, self.tree_center, IMAGE[1] / 2)

    def load_data(self, file):
        duplicates = []
        for led in json.loads(file.read_text()):
            if led['led'] == -1:
                continue
            if led['led'] in self.snapl:
                duplicates.append(SnapLine(led['x'], led['y'], led['led'], self))
            else:
                self.snapl[int(led['led'])] = SnapLine(led['x'], led['y'], led['led'], self)

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
    def image_center_x(self) -> float:
        """
        Return the pixel position representing the image center. This pixel represents the origin of the tree.
        The exact position of the origin will move over time with more Snaps processed
        :return: pixel position
        """
        if hasattr(self, 'camera_pos'):
            return self.camera_pos.origin[0]
        return self.tree_center

    @property
    def image_center_y(self) -> float:
        """
            Return the pixel position representing the image center. This pixel represents the origin of the tree.
            In the Z axis the origin will be half height of the tree.
            In the inital images, the image center is placed in the middle of the picture
            The exact position of the origin will move over time with more Snaps processed
            :return: pixel position
        """
        if hasattr(self, 'camera_pos'):
            return self.camera_pos.origin[1]
        return IMAGE[1] / 2

    @property
    def tree_center(self) -> int:
        """
        Get the pixel in which the tree center is expected.
        This pixel has the lowest mean error when checking distances to active leds. (most in the middle pixel)
        This function is only used to estimate the origin in the raw data.
        As soon as a camera position is available the camera center estimation should be used.
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
        """
        List of relative led distances based on the raw image.
        :return:
        """
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
        return DataFrame([[0, -self.camera_distance_estimation(), 0]])

    def pixel_phi(self, snap: SnapLine) -> float:
        """
        Return angle between the line from the camera to the center of the tree
        :param snap: A snap line in the original image
        :return: angle in radians
        """
        return radians((snap.y - self.image_center_x) * LENS_ANGLE[0] / IMAGE[0])

    def pixel_theta(self, snap: SnapLine) -> float:
        """
        Return the angle between de line through the led and the center of the image.
        :param snap: A snap line in the original image
        :return: angle in radians
        """
        return radians((self.image_center_y - snap.x) * LENS_ANGLE[1] / IMAGE[1])

    def angle_extremes(self) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        """
        Get the outer angles in de picture (in radians)
        :return: ((x_min, y_min), (x_max, y_max))
        """
        leds = [led for led in self.snapl.values() if led.reliable]
        if not self._angle_extremes:
            self._angle_extremes = ((min([self.pixel_phi(led) for led in leds]),
                                     min([self.pixel_theta(led) for led in leds])),
                                    ((max([self.pixel_phi(led) for led in leds]),
                                      max([self.pixel_theta(led) for led in leds]))))
        return self._angle_extremes

    def camera_distance_estimation(self) -> float:
        """
        Get the camera distance in units. One unit is the expected distance between tree center and most outer led."
        :return:
        """
        angle = max(abs(self.angle_extremes()[0][0]), abs(self.angle_extremes()[1][0]))
        return 1 / sin(angle)

    def refit_center_pixel(self):
        """
        Use the model of pixels to determine what the origin in the image should be.
        :return:
        """
        pixels = rotate_pixel_dict(pixel_positions.latest(), self.camera_pos.phi_estimate)
        positive = [pixels[p] for p in pixels if pixels[p].y >= 0 and p in self.snapl]
        negative = [pixels[p] for p in pixels if pixels[p].y <= 0 and p in self.snapl]
        upper = min(positive, key=lambda p: p.y)
        lower = max(negative, key=lambda p: p.y)

        a = self.snapl[upper.id]
        b = self.snapl[lower.id]
        self.camera_pos.origin = ((a.y + b.y) / 2, self.camera_pos.origin[1])

    def refit_camera(self):
        self.refit_center_pixel()

        pixels = rotate_pixel_dict(pixel_positions.latest(), self.camera_pos.phi_estimate)

        snap = [snap for snap in self.snapl.values() if snap.reliable]
        """
        Find 5 snapped pixels on both sides of the tree with most extreme (biggest) angles.
        Esta the camera distance based on these leds 
        """
        extremes = sorted(snap, key=lambda s: self.pixel_phi(s))

        distances = []
        for snap in extremes[:5] + extremes[-5:]:
            try:
                pixel = pixels[snap.id].coord
                distances.append(pixel[0] + pixel[1] / self.pixel_phi(snap))
            except LookupError:
                pass

        self.camera_pos.coord = [median(distances), 0, 0]
