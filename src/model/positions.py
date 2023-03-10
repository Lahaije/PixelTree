import numpy as np
from typing import Dict
import pandas as pd

from model.camera import CameraPosition
from model.spherical_coordinate import SphereCoord


class Pixel(SphereCoord):
    def __init__(self, led_id: int,  x: float, y: float, z: float):
        self.id = led_id
        super().__init__(x, y, z)

    def __add__(self, other):
        if isinstance(other, Pixel):
            return Pixel(self.id, self.x + other.x, self.y + other.y, self.z + other.z)
        else:
            return Pixel(self.id, self.x + other[0], self.y + other[1], self.z + other[2])

    def __truediv__(self, other):
        return Pixel(self.id, self.x/other, self.y/other, self.z/other)


class CameraInfo:
    """
    This class holds all information available for all camera positions
    """
    def __init__(self):
        self.iteration = 0
        self.main_camera = None  # The main camera is the first camera added. All other cameras are referenced to this camera
        self.camera_pos = pd.DataFrame(columns=['x', 'y', 'z', 'name', 'origin_x', 'origin_y', 'iteration'])

    def add_camera(self, cam: CameraPosition):
        """
        Add a possible camera position
        :param cam: Camera position
        :return:
        """
        if not self.main_camera:
            self.main_camera = cam.name

        df = cam.data_frame
        df['iteration'] = self.iteration
        self.camera_pos = pd.concat(self.camera_pos, df)


class PixelPositions:
    def __init__(self):
        self.iteration = 0
        self.data: Dict[int, Dict[int, Pixel]] = {}

    def push(self, data: Dict[int, Pixel]):
        self.data[self.iteration] = data
        self.iteration += 1

    def latest(self) -> Dict[int, Pixel]:
        if self.iteration == 0:
            raise LookupError('No positions are available')
        return self.data[self.iteration-1]

    def scale(self, iteration):
        all_x = []
        all_y = []
        for pixel in pixel_positions.data[iteration].values():
            all_x.append(abs(pixel.x))
            all_y.append(abs(pixel.y))

        scale = max(all_x + all_y)
        print(f"SCALE {scale}")

        for pixel in pixel_positions.data[iteration].values():
            pixel.x = pixel.x / scale
            pixel.y = pixel.y / scale


pixel_positions = PixelPositions()


def scale_pixels():
    """
    Scale all pixels back to values between 1 and -1
    :return:
    """
    pixel_positions.scale(pixel_positions.iteration -1)

