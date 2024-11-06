"""
This file contains loaders for data.
Loaders should be fast and this file is not allowed to import expensive modules

The idea is to make an export once for all snaps, and further download re-load the data using the matching loader.

The loader file should not import from the exporter, since the exportor imports from the loader to regenerate the
data for a step in de process.

"""
import json
from pathlib import Path
from typing import List
import pandas as pd

from analyze_data import DataContainer, optimize_led_strings


def load_all_data_container(optimize=False) -> List[DataContainer]:
    """
    Load all data from the snaps.
    If optimize is set to True, every snap will take the most accurate estimate for a led position.
    Optimizing will try to fit led in connected strings.
    """

    snaps = []
    for folder in (Path(__file__).parents[1] / 'snap').glob('*'):
        if folder.stem in ('backup',):
            continue
        snaps.append(DataContainer(folder))
        if optimize:
            optimize_led_strings(snaps[-1])

    return snaps


def load_vertical_positions() -> pd.DataFrame:
    data = {}
    for folder in (Path(__file__).parents[1] / 'snap').glob('*'):
        if folder.stem in ('backup',):
            continue

        data[folder.stem] = json.loads((folder / 'center_led_pos.json').read_text())

    return pd.DataFrame(dict([(k, pd.Series(v)) for k, v in data.items()]))


if __name__ == "__main__":
    load_vertical_positions()
