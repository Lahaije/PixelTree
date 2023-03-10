import requests
from requests.exceptions import ChunkedEncodingError, ReadTimeout
from typing import List
import time

from config import NUM_PIXELS


class Frame:
    """
    a Frame contains a single scene for the pixeltree
    """
    def __init__(self):
        self.leds = [[0]*3] * NUM_PIXELS

    def to_binary(self):
        binary = bytearray()
        for led in self.leds:
            for k in range(3):
                binary.append(led[k])

        return binary


class PixelTree:
    def __init__(self):
        self.buffer_size = 10
        self.fps = 9
        self.frames = []
        self.timeout = 2
        self.url = 'http://192.168.1.100'

    @property
    def headers(self):
        return {'Content-Type': 'application/octet-stream'}

    def append_buffered_frame(self, frame: Frame):
        self.frames.append(frame)
        if len(self.frames) == self.buffer_size:
            self.push_frames(self.frames)
            self.frames = []

    def send_frame(self, frame: Frame, buffered=True):
        if buffered:
            self.append_buffered_frame(frame)
        else:
            self.push_frames([frame])

    def to_binary(self, frames: List[Frame]):
        """
        Convert a list of frames to the binary format as used on esp32.
        :param frames: List of Frames
        :return: Binary string.
        """
        data = bytearray()
        data.append(len(frames))
        data.append(self.fps)
        for frame in frames:
            data += frame.to_binary()

        return data

    def push_frames(self, frames: List[Frame]):
        try:
            r = requests.post(url=self.url,
                              data=self.to_binary(frames),
                              headers=self.headers,
                              timeout=2)
            if r.status_code != 200:
                print(r.text)
        except ConnectionResetError as e:
            print(f'RESET error {e}')
        except ChunkedEncodingError as e:
            print(f'CHUNK error {e}')
        except ReadTimeout as e:
            print(f'READ timeout {e}')


pixelTree = PixelTree()


if __name__ == "__main__":
    start = time.time()
    col = 0
    colpos = 0

    while True:
        if col == 200:
            col = 0
            colpos += 1
            if colpos == 3:
                colpos = 0

        color = [col, 0, 0], [0, col, 0], [0, 0, col]

        col += 1

        f = Frame()

        for n in range(int(NUM_PIXELS/2)):
            f.leds[n * 2] = color[colpos]
            f.leds[n * 2 + 1] = [0, 0, 0]

        pixelTree.send_frame(f)
