from math import pi
from typing import Tuple

from model.snap import RawSnapData


def triangulate(cam1: RawSnapData, cam2: RawSnapData, cam3: RawSnapData) -> Tuple[float, float, float]:
    """
    Make a triangulated estimate of the estimated angles between 3 camera positions
    :param cam1: Raw ImageData object
    :param cam2: Raw ImageData object
    :param cam3: Raw ImageData object
    :return: cam1 -> cam2, cam2 -> cam3, cam3 cam1.
    """
    a = cam1.estimate_angle(cam2)
    b = cam2.estimate_angle(cam3)
    c = cam3.estimate_angle(cam1)

    dif = 2 * pi
    data = (0.0, 0.0, 0.0)
    for i in range(0, 2):
        for j in range(0, 2):
            for k in range(0, 2):
                sum_deg = a[i] + b[j] + c[k]
                if sum_deg > 3 * pi:
                    sum_deg = sum_deg / 2

                if abs(2 * pi-sum_deg) < abs(dif):
                    dif = 2 * pi - sum_deg
                    x = a[i] * (1 + dif/(2 * pi))
                    y = b[j] * (1 + dif/(2 * pi))
                    z = c[k] * (1 + dif/(2 * pi))
                    data = x, y, z
    return data
