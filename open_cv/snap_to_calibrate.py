from pathlib import Path
from time import sleep

from cv2 import imwrite


from webcam import Webcam


if __name__ == "__main__":

    for counter in range(20):
        print(f'Making webcam picture {counter}')

        im = Webcam.snap()

        imwrite(str(Path(__file__).parent / f'cam_{counter}.jpg'), im)

        sleep(1)