from pathlib import Path
from typing import List
import statistics

import matplotlib.pyplot as plt
import numpy as np
from config import NUM_PIXELS
from pandas import DataFrame


from analyze_data import DataContainer


def load_all_data() -> List[DataContainer]:
    snaps = []
    for folder in (Path(__file__).parents[1] / 'snap').glob('*'):
        if folder.stem in ('backup',):
            continue
        snaps.append(DataContainer(folder))

    return snaps


def count_times_leds_occurs(snaps: List[DataContainer]):
    all_id = {}
    for cont in snaps:
        for led in cont.data.values():
            if not led.active:
                continue
            try:
                all_id[led.led_id] += 1
            except KeyError:
                all_id[led.led_id] = 1

    return all_id


def estimate_led_height(snaps: List[DataContainer], num_rotatations=2, median_width=3) -> DataFrame:
    """
    Estimate the height of each led, using all available data.
    This function compares the led heights of all detected leds in an image.
    Using existing estimates of the height of the highest and lowest led in the image, the heights of all leds in the
    images are estimated based on the complete tree height. (Complete tree has height of 1)
    When estimating the  height of a single led, the median is taken from the led, and X leds on either side and all images containing all these leds.


    :param: snaps : List of all DataContainers
    :param: num_rotations : Number of times the median is recycled to improve height detection.
    :param: median_width : How many neighbour leds on each side are considered when estimating the height.
    Returns a dataframe with 1 height for each led.
    """
    # median Dataframe holds the most probable height of a led. (Scaled between 0 and 1.)
    # In case no median_score is provided, lineair scaling of all leds is assumed for a start point.
    median_df = DataFrame({'median': [(_ / NUM_PIXELS) for _ in range(NUM_PIXELS)]}, dtype=np.float64)

    def _do_calculate():

        score = {}
        for cont in snaps:
            """
            Pictures have the height "reversed."
            Pixel 0.0 is the top left corner. 
            Due to picutures having the top getting the lower X value, min, and max are reversed. 
            """
            heights = cont.sort_leds_by_height()
            min_h = heights[-1].x
            max_h = heights[0].x
            low = median_df['median'][heights[-1].led_id]
            high = median_df['median'][heights[0].led_id]

            for i in range(len(heights)):
                scaled_height = (heights[i].x - min_h) / (max_h - min_h)
                tree_height = scaled_height * (high - low) + low
                try:
                    score[heights[i].led_id].append(tree_height)
                except KeyError:
                    score[heights[i].led_id] = [tree_height]

        for i in range(NUM_PIXELS):
            lst = []
            for led in range(i - median_width, i + median_width):
                try:
                    lst.extend(score[led])
                except KeyError:
                    pass
            try:
                median_df['median'][i] = statistics.median(lst)
            except KeyError:
                pass
        return median_df

    def _min_max_scaling(series):
        return (series - series.min()) / (series.max() - series.min())

    for _ in range(num_rotatations):
        _do_calculate()
        median_df = _min_max_scaling(median_df)

    return median_df


SNAPS = load_all_data()

HEIGHT = estimate_led_height(SNAPS)['median']  # Typing hint index = int, value = float

"""
Fill the Height estimations in the snap containers.
"""

for cont in SNAPS:
    for led in cont.data.values():
        if HEIGHT[led.led_id] > cont.estimate.max_height:
            cont.estimate.max_height = HEIGHT[led.led_id]
            cont.estimate.top_led_x = led.x
        if HEIGHT[led.led_id] < cont.estimate.min_height:
            cont.estimate.min_height = HEIGHT[led.led_id]
            cont.estimate.bot_led_x = led.x


if __name__ == "__main__":
    all_snaps = load_all_data()
    counts = count_times_leds_occurs(all_snaps)
    sorted = estimate_led_height(all_snaps)

    plt.plot(sorted['median'])
    plt.ylabel('Height')
    plt.xlabel('Led Number')
    plt.show()

    print('')
