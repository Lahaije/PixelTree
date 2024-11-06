"""
This file will check all SNAPS and calculate the relative led id to draw a vertical line
It calculates which led in the image is exactly in the center of the tree.

In case the led detection fails on to many leds in the center when the string crosses the center,
the led will be skipped.
2 leds in the center list are not always exactly 1 loop apart.
Led strings might follow the tree branch resulting in a few leds seen as being on the center.
It is also possible a loop is completely missed. This results in the angle between 2 leds not being 2pi, but 4,6, or 8 pi.
"""
from typing import Tuple

import pandas as pd
import numpy as np
import math

from config import NUM_PIXELS
from loader import load_vertical_positions


def get_main_direction(df: pd.DataFrame) -> int:
    """
    Return -1 or 1 dependent if the most common direction in the dataframe is clockwise or not.
    """
    directions = df.map(lambda x: x[1] if isinstance(x, list) else 0)
    i, c = np.unique(directions, return_counts=True)
    out = pd.Series(c, index=i)
    if out[-1] > out[1]:
        return -1
    return 1


def filtered_vertical_positions(direction: int, df: pd.DataFrame, min_distance=10) -> pd.DataFrame:
    """
    Filter the position dataframe. Remove all entries not following the direction and remove leds clos together
    : param direction: Filter only leds which cross in the desired direcion
    : param df: dataframe
    : param min_distance: Filter leds close together
    """
    def dir_filter(x):
        try:
            if x[1] == direction:
                return x[0]
        except TypeError:
            pass
        return np.nan

    filtered = df.map(dir_filter)

    for series_name, series in filtered.items():
        position = series.dropna().reset_index(drop=True)
        for i in range(len(position)):
            count = 1
            try:
                while position[i+count] - position[i+count-1] < min_distance:
                    count += 1
            except (KeyError, TypeError):
                pass
            if count > 1:  # remove values close together
                position[i+count-1] = sum(position[i:i+count])/count
                for _ in range(count-1):
                    position[i + _] = np.nan
        filtered[series_name] = position.dropna().reset_index(drop=True)

    return filtered


def angle_estimates(direction: int, df: pd.DataFrame) -> pd.DataFrame:
    """
    Make a dataframe containing an angle estimate for each led for each snapped picture
    """
    led_angle_data = pd.DataFrame()
    for series_name, series in df.items():
        data = np.full(NUM_PIXELS, np.nan)
        for c in range(len(series.dropna())-1):
            first = series[c]
            last = series[c+1]
            angle = direction * 2 / (last - first)
            for lid in range(math.floor(first), math.ceil(last)+1):
                data[lid] = angle
        led_angle_data[series_name] = data

    return led_angle_data


def angles_dataframe() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Create a dataframe witn NUMPIXEL rows.
    For each snapped image a column is added.
    In each column an estime of the rotation angle of the led string around the tree is calculated.

    Return:
        verticals : Each column of the dataframe contains a list of led id's which are vertical aligned
        estimate : Each column contains an estimate for the angle the led rotates around the tree
    """
    pos = load_vertical_positions()
    main_dir = get_main_direction(pos)
    verticals = filtered_vertical_positions(main_dir, pos)
    estimate = angle_estimates(main_dir, verticals)
    estimate['median'] = estimate.median(axis=1)
    return verticals, estimate


if __name__ == "__main__":
    verticals, estimate = angles_dataframe()
    test = estimate['median']
