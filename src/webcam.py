from cv2 import VideoCapture, imwrite, imread, imshow, waitKey, destroyWindow
from numpy import ndarray

from config import storage

"""
Methods to use the webcam, create, store and read back images.
"""


class Webcam:
    cam_port = 0
    cam = VideoCapture(cam_port)

    @staticmethod
    def snap() -> ndarray:
        success, image = Webcam.cam.read()
        if not success:
            raise RuntimeError('Something went wrong while making image')
        return image


def store_im(name, image):
    location = storage / f'{name}.png'
    storage.mkdir(exist_ok=True, parents=True)
    imwrite(str(location), image)


def read_im(name, folder=''):
    return imread(str(storage / folder / f'{name}.png'))


def show_im(image):
    imshow('image', image)
    waitKey(0)
    destroyWindow('image')


if __name__ == "__main__":
    show_im(Webcam.snap())
