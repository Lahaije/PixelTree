from math import pi
from typing import Dict, Tuple, List

from model.snap import RawSnapData
from model.positions import Pixel
from caculations import estimate_angle, all_intersection
from model.transformations import rotate_xy, rotate_pixel_dict
from config import NUM_PIXELS


def calc_best_right_angle(c1, c2, c3):
    """
    get the most probable angles between the 3 inputs
    return c1 -> c2, c2 -> c3, c3 -> c1
    """
    a = estimate_angle(c1, c2)
    b = estimate_angle(c2, c3)
    c = estimate_angle(c3, c1)

    angles = {}

    for i in range(2):
        for j in range(2):
            for k in range(2):
                total = a[i] + b[j] + c[k]
                angles[abs(total - 2 * pi)] = [2 * pi * a[i] / total, 2 * pi * b[j] / total, 2 * pi * c[k] / total]

    return angles[min(angles.keys())]


def intersection_in_sphere_frame(cam1: RawSnapData, cam2: RawSnapData):
    """
    Get the intersections between cam1 and cam2.
    The coordinates of the response are based on the standard sphere reference frame.
    The used camera angles are the phi estimates as stored with the camera.
    :param cam1:
    :param cam2:
    :return:
    """
    data = all_intersection(cam1, cam2, cam2.camera_pos.phi_estimate - cam1.camera_pos.phi_estimate)
    return rotate_pixel_dict(data, -cam1.camera_pos.phi_estimate)


def triangulate_angled(cam1: RawSnapData, cam2: RawSnapData, cam3: RawSnapData) -> Dict[int, Pixel]:
    """
    Make a triangulated estimation of the pixel positions
    :param cam1: Raw ImageData object
    :param cam2: Raw ImageData object
    :param cam3: Raw ImageData object
    :return: Array with calculated led positions.
    """

    d = [intersection_in_sphere_frame(cam1, cam2),
         intersection_in_sphere_frame(cam2, cam3),
         intersection_in_sphere_frame(cam1, cam3)]

    data = {}
    for key in range(NUM_PIXELS):
        p = Pixel(key, 0, 0, 0)
        num = 0
        for data_points in d:
            if key in data_points:
                p += data_points[key]
                num += 1
        if num > 0:
            data[key] = p / num

    return data


def triangulate(cam1: RawSnapData, cam2: RawSnapData, cam3: RawSnapData) -> Tuple[float, float, float]:
    """
    Make a triangulated estimate of the estimated angles between 3 camera positions
    :param cam1: Raw ImageData object
    :param cam2: Raw ImageData object
    :param cam3: Raw ImageData object
    :return: cam1 -> cam2, cam2 -> cam3, cam1 cam3.
    """
    a = estimate_angle(cam1, cam2)
    b = estimate_angle(cam2, cam3)
    c = estimate_angle(cam3, cam1)

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
