from math import cos, sin, inf, pi
from typing import Dict, Tuple

import numpy
import numpy as np
from scipy.signal import argrelmax, find_peaks

from model.snap import RawSnapData
from model.positions import Pixel
from model.transformations import rotate_xy


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
    pos1 = cam1.camera_pos.coord
    pos2 = rotate_xy(cam2.camera_pos.coord, phi)
    """
    Line equation X cos(a) + Y sin(a) + c = 0
    aX + bY + c = 0
    given the camera position (x, y) we van solve
    c = -x*cos(a) -y*sin(a) 
    """
    alfa = cam1.pixel_phi(cam1.snapl[led_id])
    beta = cam2.pixel_phi(cam2.snapl[led_id])

    a1 = sin(alfa)
    b1 = cos(alfa)
    c1 = -pos1[0]*a1 - pos1[1]*b1

    a2 = sin(beta + phi)
    b2 = cos(beta + phi)
    c2 = -pos2[0]*a2 - pos2[1]*b2

    try:
        # Solve Cramer's rule
        x = ((b1 * c2 - b2 * c1) / (a1 * b2 - a2 * b1))
        y = ((c1 * a2 - c2 * a1) / (a1 * b2 - a2 * b1))
        return x, y
    except ZeroDivisionError:
        return inf, inf


def angle_fit_data(cam1: RawSnapData, cam2: RawSnapData, num_test_angles=500) -> numpy.ndarray:
    """
    Generate data to test what is the most probable angle 2 cameras make with each other.
      The other camera is virtually rotated 360 degrees around the origin.
      The first test is both camera's on the same side (phi = 0)
      For each step a score is calculated. This score represents how well all Pixels fit in the unity circle.
      A higher score is a better fit.
    :param cam1: Base camera
    :param cam2: Data snap to test against.
    :param num_test_angles: the number of tests steps to take when making 1 full rotation
    :return: Array. Each element holds angle phi and a score for the fit of the angle
    """
    result = np.ndarray(shape=(num_test_angles, 2), dtype=float)
    for i in range(0, num_test_angles):
        phi = i * 2 * pi / num_test_angles
        result[i] = (phi, 0)

        for led in cam1.snapl.values():
            if led.reliable and led.id in cam2.snapl and cam2.snapl[led.id].reliable:
                x, y = get_intersection_coord(cam1, cam2, phi, led.id)

                dist = x*x + y*y
                if dist < 1:
                    result[i, 1] += 1
                else:
                    result[i, 1] += 1/dist

    return result


def estimate_angle(cam1: RawSnapData, cam2: RawSnapData) -> Tuple[float, float]:
    """
    Make an estimation of the most likely angles 2 camara positions make with each other.
    :param cam1: Base camera
    :param cam2: Second camera. The reported angle is the angle cam2 makes with cam1
    :return: Tuple [best angle, second best angle.]
    """
    data = angle_fit_data(cam1, cam2)
    peaks, _ = find_peaks(data[:, 1])
    maxima = [data[p] for p in peaks]
    sorted_max = sorted(maxima, key=lambda m: m[1], reverse=True)

    best = sorted_max[0][0]
    second = sorted_max[1][0]
    if best > pi:
        best = best - 2 * pi
    if second > pi:
        second = second - 2 * pi

    return best, second


def all_intersection(cam1: RawSnapData, cam2: RawSnapData, angle, max_dist=2) -> Dict[int, Pixel]:
    """
    Calculate the coordinates of leds visible by 2 cameras with a given angle between the camera's.
    The coordinates are referenced to the frame of the first camera.
    :param cam1: LedData camera position
    :param cam2: other LedData camera position
    :param angle: desired angle between the 2 camera's
    :param max_dist: only leds with coordinates smaller than max_dist are added in the returned dict
    :return: Dict. Key is the led id, value is a tuple of x, y, z
    """
    data = {}
    for key in cam1.snapl.keys():
        if key in cam2.snapl:
            x, y = get_intersection_coord(cam1, cam2, angle, key)
            if -max_dist < x < max_dist and -max_dist < y < max_dist:
                data[key] = Pixel(key, x, y, 0)
    return data
