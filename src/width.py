import numpy as np
import pandas as pd
from statistics import mean, median
from scipy.optimize import curve_fit
from typing import Generator, Tuple
import matplotlib.pyplot as plt

from analyze_data import DataContainer
from config import IMAGE, NUM_PIXELS
from height import SNAPS, HEIGHT


def estimate_distance(snap: DataContainer):
    """
    Estimate the distance of the camera to the tree
    """
    store = {}
    for led in snap.data.values():
        store[led] = abs(HEIGHT[led.led_id] - 0.5)

    center_tree = mean([k.x for k, v in sorted(store.items(), key=lambda item: item[1])][:10])

    x = []
    y = []
    for led in snap.data.values():
        x.append((led.x - center_tree) / IMAGE[1])
        y.append(HEIGHT[led.led_id])

    def fun(x, h, d):
        return h + d * np.tan(x)

    popt, pcov = curve_fit(fun, x, y)

    print(f"{snap.snap_name.stem} Camera height = {popt[0]:.2f} Dist = {popt[1]:.2f}")
    snap.estimate.camera_distance = popt[1]


def estimate_led_radius(snap: DataContainer) -> Generator[Tuple[int, float], None, None]:
    """
    Estimate the distance of the led to tree trunk.
    """
    for led in snap.data.values():
        if abs(snap.estimate.scaled_led_height(led) - HEIGHT[led.led_id]) > 0.1:
            continue  # Exclude leds far away from estimation

        dist = abs(snap.m * led.x + snap.c - led.y) * snap.estimate.pixelscale
        yield led.led_id, dist


def estimate_led_width(plot_raw_data=False):
    """
    Calculate an estimate of a smoothed distance of all leds to the trunk of the tree.
    For all detected leds the distance to the trunk is added to a dataframe.
    When the trunk, led and ca
    """

    df = pd.DataFrame(index=np.arange(NUM_PIXELS), columns=[snap.snap_name.stem for snap in SNAPS])
    for snap in SNAPS:
        for lid, dist in estimate_led_radius(snap):
            df.loc[lid, snap.snap_name.stem] = dist

    def average_above_median(row):
        """
        Calculate the average distance of all leds above the median.
        This function eliminates leds close to the trunk to be included in the distance estimation.
        Leds close to the trunk are below the median value and will not be considered when calculating the max distance.
        By averaging led distances far away from the trunk, miss detected leds far away will probably be dampened.
        """
        el = [x for x in row if x > 0]
        if len(el) == 0:
            return np.nan
        med = median(el)

        return mean([x for x in el if x >= med])

    df['above'] = df.apply(average_above_median, axis=1)

    if plot_raw_data:
        plt.plot(np.linspace(0, 1, 600), df['above'])

    series = df['above'].dropna()

    z = np.polyfit(HEIGHT[list(series.index)], series, 5)
    p = np.poly1d(z)

    return pd.Series([p(i) for i in np.linspace(0, 1, 600)])


WIDTH = estimate_led_width()


if __name__ == "__main__":
    """
    buur = SNAPS[0]
    for i in range(600):
        try:
            led = buur.data[i]
            print(f"{led.led_id} {HEIGHT[i]:.2f} {buur.estimate.scaled_led_height(led)}")
        except KeyError:
            pass
    """
    plt.plot(np.linspace(0, 1, 600), HEIGHT, "b--")
    plt.plot(np.linspace(0, 1, 600), WIDTH, "r--")
    plt.title('Width')

    plt.show()
