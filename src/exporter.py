"""
This file contains exporters for data.
Exporting data may import expensive modules.

The idea is to make an export once for all snaps, and further download re-load the data using the matching loader.
"""
import json

from config import storage, NUM_PIXELS
from pictures import show_data

from loader import load_all_data_container

# Create PNG images


def create_show_data_png():
    for folder in storage.glob('*'):
        show_data(folder.name, 5, True)


# Create data files

def export_center_leds(optimize=False):
    for snap in load_all_data_container(optimize):
        pos = snap.snap_name / 'center_led_pos.json'

        data = json.dumps([[round(i[0], 2), i[1]] for i in snap.center_led_list()])

        pos.write_text(data)

        print(f"{snap.snap_name.stem} {data}")


if __name__ == "__main__":
    export_center_leds(True)