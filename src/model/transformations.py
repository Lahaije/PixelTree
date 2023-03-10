from math import cos, sin
from typing import Dict, Union

import numpy as np

from model.positions import Pixel


def rotation_matrix(angle: float, axis='z') -> np.array:
    if axis == 'z':
        return np.array([[cos(angle), -sin(angle), 0],
                         [sin(angle), cos(angle), 0],
                         [0, 0, 1]])
    if axis == 'x':
        return np.array([[1, 0, 0],
                         [0, cos(angle), -sin(angle)],
                         [0, sin(angle), cos(angle)]])

    if axis == 'y':
        return np.array([[cos(angle), 0, sin(angle)],
                         [0, 1, 0],
                         [-sin(angle), 0, cos(angle)]])

    raise RuntimeError(f'Rotation "{axis}" not supported')


def rotate_xy(vector: Union[np.ndarray, Pixel], angle: float) -> np.ndarray:
    if isinstance(vector, Pixel):
        vector = vector.coord
    if len(vector) != 3:
        raise RuntimeError(f'Vector "{vector}" should represent x, y, z')
    return np.dot(vector, rotation_matrix(angle))


def rotate_pixel_dict(data: Dict[int, Pixel], phi: float) -> Dict[int, Pixel]:
    """
    Return the same data in a rotated frame of reference
    :param data: Dict of pixels
    :param phi: rotations angle. Rotation takes place in xy, frame
    :return:
    """
    result = {}
    for key, pix in data.items():
        rot = rotate_xy(pix, phi)
        result[key] = Pixel(key, rot[0], rot[1], rot[2])
    return result
