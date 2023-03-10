from math import sqrt, acos
import numpy as np
from numpy import sign
from typing import Optional


class SphereCoord:
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z
        self._distance: Optional[float] = None
        self._theta: Optional[float] = None
        self._phi: Optional[float] = None

    def __setattr__(self, name, value):
        if name in ('x', 'y', 'z'):
            self._distance = None

        super(SphereCoord, self).__setattr__(name, value)

    def __getitem__(self, item):
        if isinstance(item, int):
            return self.coord[item]

        raise RuntimeError(f'Unexpected call to getitem for item {item}')

    @property
    def distance(self) -> float:
        # Distance to origin
        if not self._distance:
            self._distance = sqrt(self.x**2 + self.y**2 + self.z**2)
        return self._distance

    @property
    def theta(self) -> float:
        if not self._theta:
            self._theta = acos(self.z/self.distance)
        return self._theta

    @property
    def phi(self) -> float:
        if not self._phi:
            self._phi = sign(self.y) * acos(self.x / sqrt(self.x**2 + self.y ** 2))
        return self._phi

    @property
    def coord(self) -> np.ndarray:
        return np.array([self.x, self.y, self.z])

    def __str__(self):
        return f"{self.__class__.__name__} ({self.x:.2f}, {self.y:.2f}, {self.z:.2f})"
