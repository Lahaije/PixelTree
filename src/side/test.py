import time
from neopixel import Color

#from snap_pixels import Snapper

from calc_pixels import Cluster
from webcam import show_im, read_im
from config import storage

if __name__ == "__main__":
    for folder in storage.iterdir():
        try:
            show_im(read_im("results", folder))
        except Exception:
            pass


    print('Make Pixels')
    name = 'fiets_90_white_4'

    Snapper(name, 'white').run()

    print("Start detection")
    start = time.time()

    c = Cluster(name)
    c.filter_by_low_score()
    c.show_results()
    print(f"done {int(time.time() - start)} seconds")
