from math import sqrt, acos
from numpy import sign
from typing import Optional


class SphereCoord:
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z
        self._distance = Optional[float]
        self._theta = Optional[float]
        self._phi = Optional[float]

    def __setattr__(self, name, value):
        if name in ('x', 'y', 'z'):
            self._distance = None

        super(SphereCoord, self).__setattr__(name, value)

    @property
    def distance(self):
        # Distance to origin
        if not self._distance:
            self._distance = sqrt(self.x**2 + self.y**2 + self.z**2)
        return self._distance

    @property
    def theta(self):
        if not self._theta:
            self._theta = acos(self.z/self.distance)
        return self._theta

    @property
    def phi(self):
        if not self._phi:
            self._phi = sign(self.y) * acos(self.x / sqrt(self.x**2 + self.y ** 2))
        return self._phi
