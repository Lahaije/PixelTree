import numpy as np
from pandas import DataFrame
from typing import List

from model.spherical_coordinate import SphereCoord


class CameraPosition(SphereCoord):
    def __init__(self, x: float, y: float, z: float, name, origin_x, origin_y):
        if x == y == 0:
            raise ZeroDivisionError('Camera position not allowed in center of tree')
        super().__init__(x, y, z)
        self.name = name
        self.origin = (origin_x, origin_y)  # pixel in the image pointing to the current origin
        self.phi_estimate = 0  # This value will get updated as soon as estimations of the camera position are available
        self.theta_estimate = 0

    @property
    def data_frame(self):
        return DataFrame({'x': self.x,
                          'y': self.y,
                          'z': self.z,
                          'name': self.name,
                          'origin_x': self.origin[0],
                          'origin_y': self.origin[1]})

    @property
    def coord(self) -> np.ndarray:
        return np.array([self.x, self.y, self.z])

    @coord.setter
    def coord(self, coord: List[float]):
        self.x = coord[0]
        self.y = coord[1]
        self.z = coord[2]
