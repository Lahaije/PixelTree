from collections import UserList
from dataclasses import dataclass
from statistics import median
from typing import Dict, List, Optional, Union
from warnings import warn
from math import cos, pi, sin, isnan
import matplotlib.pyplot as plt
import math
import numpy as np
import pandas as pd
import statistics

from config import NUM_PIXELS
from vertical_align import angles_dataframe
from width import WIDTH

class Theta(UserList):
    """
    Theta is a list of angles. In the end it will hold 1 value for each pixel.
    """
    def interpolate(self, led_id: float) -> float:
        """
        Interprolate the angle of a given led_id in the Theta array to calculate the angle.
        """
        try:
            min_val = self[math.floor(led_id)]
            max_val = self[math.ceil(led_id)]
            if abs(min_val - max_val) > 1:  # Value is wrapping around at 2 pi.
                if min_val < 1:
                    max_val = max_val - 2
                else:
                    min_val = min_val - 2

            return uni_theta(min_val + led_id % 1 * (max_val - min_val))
        except TypeError:
            raise ValueError('Theta not found')

THETA: Theta[Optional[float]] = Theta(None for i in range(NUM_PIXELS))

@dataclass
class FullRotation:
    start: int  # Led ID of start of rotation
    end: int  # Led ID of end of rotation
    variance: float  # Sum of the variance of detection. (lower is more accurate)

    def angles(self) -> List[float]:
        angles = [0.0]
        for i in range(self.end - self.start - 1):
            angles.append(angles[i] + ANGLES['median'][self.start + i])
        return angles

    def get_angle_of_led(self, pos: float):
        """
        Get the angle of a led pos estimated in the fullRotation frame of reference.
        The angle is 0 at the start, and 2 at the end.
        """
        return (pos - self.start) / (self.end - self.start) * 2


@dataclass
class CamPos:
    angle: float
    fits: List[float]

    def precision(self) -> Optional[float]:
        """
        Estimation how well the camera angle matches all it's detected leds.
        """
        if not self.fits:
            return None
        return sum([(_ - self.angle) ** 2 for _ in self.fits]) / len(self.fits)


campos: Dict[str, CamPos] = {}


def x(r: float, theta: float) -> float:
    return r * cos(theta + 2.9)


def y(r: float, theta: float) -> float:
    return r * sin(theta + 2.9)


def uni_theta(theta: float) -> float:
    """
    Keep theta as unit circle theta between 0 and 2
    (Assume theta to no more than 1 circle out of sync. (theta between -2 and 4))
    """
    if 0 < theta < 2:
        return theta
    if theta < 0 :
        return theta + 2
    return theta - 2

verticals, ANGLES = angles_dataframe()


def find_rotatation_with_smalest_variance(threshold=30) -> FullRotation:
    """
    Find the led rotation with the smalest variance.
    A led rotation is a increasing series of leds making 1 full loop around the tree.
    A rotation visable in just 1 image and no other would have a variance of 0.
    To filter, the threshold should be given as a percentage.
    Only rotations seen in more than threshold percent of the images are considered for this function.

    :param threshold: percentage of images required to contain data for detection.
    """
    # Take only rows with appear in at least 30 % of the images.
    sums = ANGLES.isna().sum(axis=1)
    sums[sums > (100 - threshold) / 100 * len(ANGLES.columns)] = 0

    if np.count_nonzero(sums) / NUM_PIXELS < 0.5:
        warn('Rotation estimation filtering more then 50% of the leds. Try lowering the threshold.')

    variance = ANGLES.var(axis=1) * sums * abs(2/ANGLES['median'])

    rotation_info: List[FullRotation] = []
    for led in range(NUM_PIXELS):
        current = led
        angle = 0
        while angle < 2:
            if sums[current] == 0:
                break  # Not possible to get the full rotation with enough camera's
            angle += abs(ANGLES['median'][current])  # increase the angle
            current += 1
        if angle < 2:
            continue
        rotation_info.append(FullRotation(led, current, sum(variance[led:current])))

    best_rotation = min(rotation_info, key=lambda r: r.variance)

    return best_rotation


INITIAL_ROTATION: Optional[FullRotation] = find_rotatation_with_smalest_variance()


def plot_led_angles():
    c_x = []
    c_y = []
    for i in range(NUM_PIXELS):
        r = WIDTH[i]
        if THETA[i]:
            theta = THETA[i]
        else:
            theta = 0

        c_x.append(x(r, theta * pi))
        c_y.append(y(r, theta * pi))

    fig, ax = plt.subplots()
    ax.scatter(c_x, c_y, s=1)

    color = {'buur2': 'b',
             'corner2': 'r',
             'haaks': 'g',
             'front5': 'c',
             'lantaarn': 'y',
             'woonkamer': 'k'}

    for series_name, series in verticals.items():
        if series_name not in color.keys():
            continue
        for i in range(len(series)):
            try:
                first = round(series[i])
                sec = round(series[i+1])
                plt.plot([c_x[first], c_x[sec]], [c_y[first], c_y[sec]], color[series_name])
            except ValueError:
                break

    for cam, col in color.items():
        c_x = x(0.3, campos[cam].angle * pi)
        c_y = y(0.3, campos[cam].angle * pi)
        ax.scatter(c_x, c_y, s=5, color=col, label=cam)
        ax.annotate(f'{campos[cam].angle:.2f}', (c_x, c_y))

    plt.savefig('../median_rotate_plot.png')
    plt.legend()
    plt.show()


def rank_cameras():
    """
    Make a list of camera's. The first camera in the list matches the rotation best.
    """
    precision = {}
    rank = {}
    low_rank = {}

    for series_name in verticals.keys():
        try:
            if not (precis := campos[str(series_name)].precision()) is None:
                precision[series_name] = precis
                continue
        except KeyError:
            pass

        diff = (ANGLES[series_name][INITIAL_ROTATION.start:INITIAL_ROTATION.end]-
                ANGLES['median'][INITIAL_ROTATION.start:INITIAL_ROTATION.end])
        score = sum(diff.abs())

        if not isnan(score):
            rank[series_name] = score
            continue

        # For series not having enough data in the correct window, we calculate a low_rank.
        # This rank involves all the rows, and is scaled to the number of rows to compare series of different length
        series = ANGLES[series_name]
        diff = series[series.notna()] - ANGLES['median'][series.notna()]
        low_rank[series_name] = sum(diff.abs()) / len(series.notna())


    return (sorted(precision.keys(), key=lambda item: item[1]) +
            sorted(rank.keys(), key=lambda item: item[1]) +
            sorted(low_rank.keys(), key=lambda item: item[1]))


def greater_index(value: Union[int, float], series: pd.Series):
    """
    Return the next index of the series where the series is greated than
    """
    return [_[0] for _ in series.items() if _[1] > value][0]


def smaller_index(value: Union[int, float], series: pd.Series):
    """
    Return the last index of the series where the series is smaller then the value
    """
    return [_[0] for _ in series.items() if _[1] < value][-1]


def between_index(lower: Union[int, float], upper: Union[int, float], series: pd.Series) -> List:
    """
    Return the indexes of a series where the values are between the provided boundaries
    """
    return [_[0] for _ in series.items() if lower < _[1] < upper]


def get_led_id_angle_from_theta(led_id: float) -> float:
    """
    Interprolate the angle of a given led_id in the THETA array to calculate the angle.
    """
    return THETA[math.floor(led_id)] + led_id % 1 * (THETA[math.ceil(led_id)] - THETA[math.floor(led_id)])

def distance_on_unity_circle(point_a: float, point_b: float) -> float:
    """
    Calculate the distance of 2 angles on the unity circle.
    The circle should be defined as angles between 0 and 2 (mimic 0 to 2 pi angles)
    and the distance is the shortest angle between both points.
    """
    dist = abs(point_a - point_b)
    if dist < 1:
        return dist

    if point_a > 1:
        return abs(point_b + 2 - point_a)
    return abs(point_a + 2 - point_b)


def fit_all_camera(threshold = 0.1):
    """
    Find most likely camera angle based on the current data in THETA
    :param threshold: The threshold is a value between 0 and 1 on how much distance 2 angles are allowed to deviate
                      before the estimation is no longer considers the points as 2 valid inputs.
    """
    for series_name, series in verticals.items():
        detected_angles = []
        for value in series.dropna():
            try:
                detected_angles.append(THETA.interpolate(value))
            except ValueError:
                pass

        if len(detected_angles) == 0:
            continue # Nothing matches

        if len(detected_angles) == 1:
            campos[str(series_name)] = CamPos(angle=detected_angles[0], fits=[])
            continue

        # Many detections. Try to fit
        est = median(detected_angles)
        filtered = list(filter(lambda dist: distance_on_unity_circle(dist, est) < 0.1, detected_angles))
        if len(filtered) < 2:
            try:
                del campos[str(series_name)]
            except KeyError:
                pass
            continue
        campos[str(series_name)] = CamPos(angle=statistics.mean(filtered), fits=filtered)


def make_initial_rotation(camera_name: str):
    """
    Find the rotation of the first camera close to the full rotation, and fill 1 rotation of leds.
    """

    center_pixels = verticals[camera_name].dropna()

    # Find the closest crossing to the start and the end of the rotation
    start = center_pixels.iloc[(center_pixels - INITIAL_ROTATION.start).abs().argsort()[:1]].index[0]
    end = center_pixels.iloc[(center_pixels - INITIAL_ROTATION.end).abs().argsort()[:1]].index[0]

    if start == end:
        # Rare occurrence, but the best fit is somewhere in the middle of the rotation.
        # Chang the start or end to make a rotation.
        warn('Fist Camera fit unreliable')
        if abs(center_pixels[start] - INITIAL_ROTATION.start) < abs(center_pixels[end] - INITIAL_ROTATION.end):
            end += 1
        else:
            start -= 1


    angle = 2 / (center_pixels[end] - center_pixels[start])
    if sum(ANGLES['median'][INITIAL_ROTATION.start: INITIAL_ROTATION.end]) < 0:
        angle = -angle # Make angle match the correct direction

    sum_angle = 0
    for i in range(math.floor(center_pixels[start]), math.ceil(center_pixels[end]) + 1 ):
        THETA[i] = sum_angle
        sum_angle = uni_theta(sum_angle + angle)

def print_campos():
    for key, cam in campos.items():
        print(f'{key} {cam.angle:.2f}')

def calculate_increasing_angle(direction:float,
                               low_id:float, high_id:float,
                               low_angle:float, high_angle:float) -> float:
    """
    Calculate the angle increases per led. The Angle wraps around between 0 and 2.
    :param direction: Main direction to rotate (positive, or negative theta)
    :param low_id: Lower led id
    :param high_id: Higher led id
    :param low_angle: Angle of lower id between 0 and 2
    :param high_angle: Angle of higher id between 0 and 2
    """
    num_leds = high_id - low_id
    if direction > 0:
        if high_angle > low_angle:
            warn('POS 1 , PLEASe check if positive angle works')
            ang_diff = high_angle - low_angle
        else:
            warn('POS 2 , PLEASe check if positive angle works')
            ang_diff = high_angle - low_angle + 2
    else:
        if low_angle > high_angle:
            ang_diff = high_angle - low_angle
        else:
            ang_diff = -(low_angle - high_angle + 2)


    return ang_diff / num_leds


def map_downwards(freedom_percentage = 40):
    """
    Fill Theta downwards.
    :param freedom_percentage: Percentage the estimated angle may differ from the angle of the camera.
                                With the first estimation based on a single Camera, this percentage should be
                                rather high to compensate for a bad first fit.
                                The percentage should also be high if just a few leds make up a full circle
    """
    # print_campos()
    # Find upper. This is the highest located led in the tree.
    for upper in range(NUM_PIXELS):
        if not THETA[upper] is None:
            break

    for led_id in range(upper - 1, 0, -1):
        for cam_name in rank_cameras():
            if upper == led_id:
                continue
            if cam_name not in campos:
                continue
            idx = between_index(led_id, led_id + 1, verticals[cam_name])

            if idx:
                expected = statistics.fmean(ANGLES['median'][led_id: upper])

                angle_per_led = calculate_increasing_angle(expected,
                                                           verticals[cam_name][idx[0]], upper,
                                                           campos[cam_name].angle, THETA[upper])

                if (1-freedom_percentage/100) < abs(angle_per_led / expected) < (1+freedom_percentage/100):
                    for i in range(upper, led_id, -1):
                        led_angle = uni_theta(THETA[i] - angle_per_led)
                        THETA[i-1] = led_angle
                    upper = led_id
                    fit_all_camera()  # refit the camera's with the extra data.
                    print(f'{cam_name} used')

    # Fill in the remaining leds with the last detected angle
    for upper in range(NUM_PIXELS):
        if not THETA[upper] is None:
            break
    for i in range(upper, 0 , -1):
        if not pd.isna(val:=ANGLES['median'][i]):
            THETA[i - 1] = THETA[i] - val
        else:
            THETA[i-1] = uni_theta(2 * THETA[i] - THETA[i + 1])


def map_upwards(freedom_percentage = 40):
    """
    Fill Theta downwards.
    :param freedom_percentage: Percentage the estimated angle may differ from the angle of the camera.
                                With the first estimation based on a single Camera, this percentage should be
                                rather high to compensate for a bad first fit.
                                The percentage should also be high if just a few leds make up a full circle
    """
    # print_campos()
    # Find lower. This is the last located led in the tree with increasing id.
    for lower in range(NUM_PIXELS - 1, 0, -1):
        if not THETA[lower] is None:
            break

    for led_id in range(lower, NUM_PIXELS):
        for cam_name in rank_cameras():
            if lower == led_id:
                continue
            if cam_name not in campos:
                continue
            idx = between_index(led_id -1, led_id, verticals[cam_name])

            if idx:
                expected = statistics.fmean(ANGLES['median'][lower : led_id])

                angle_per_led = calculate_increasing_angle(expected,
                                                           lower, verticals[cam_name][idx[0]],
                                                           THETA[lower], campos[cam_name].angle)

                if (1-freedom_percentage/100) < abs(angle_per_led / expected) < (1+freedom_percentage/100):
                    for i in range(lower, led_id):
                        led_angle = uni_theta(THETA[i] + angle_per_led)
                        THETA[i+1] = led_angle
                    lower = led_id
                    fit_all_camera()  # refit the camera's with the extra data.
                    print(f'{cam_name} used')

    # Fill in the remaining leds with the last detected angle
    for lower in range(NUM_PIXELS - 1, 0, -1):
        if not THETA[lower] is None:
            break

    for i in range(lower, NUM_PIXELS -1):
        if not pd.isna(val:=ANGLES['median'][i]):
            THETA[i + 1] = THETA[i] + val
        else:
            THETA[i + 1] = uni_theta(2 * THETA[i] - THETA[i - 1])


def map_led_angles_using_camera():
    ranked_camera = rank_cameras()
    print(ranked_camera)

    make_initial_rotation(ranked_camera[0])
    fit_all_camera()

    map_downwards(40)
    map_upwards(40)


if __name__ == "__main__":
    map_led_angles_using_camera()
    plot_led_angles()
