from typing import Tuple

from config import storage, IMAGE

import cv2


cv2_color = {
    'red': (0, 0, 255),
    'green': (0, 255, 0),
    'blue': (255, 0, 0),
    'purple': (255, 0, 255),
    'yellow': (0, 255, 255)
}


class DataPlot:
    def __init__(self, snap_name):
        self._data = None
        self.scale = 1
        self.snap_name = snap_name
        self.img = cv2.imread(str(storage / snap_name / f'all.png'))

    def circle(self, x, y, color, radius=1):
        cv2.circle(self.img, self.scale_x_y(x, y), radius * self.scale, cv2_color[color], 1)

    def plot_led(self, x, y, color: str, led_id):
        """
        Draw a circle around the expected led location and print the id above it.
        :param x:
        :param y:
        :param color:
        :param led_id:
        :return:
        """
        self.circle(x, y, color)
        self.text(x, y, color, led_id)

    def rescale(self, scale: float):
        """
        Rescale the image with factor scale
        :param scale: Float
        :return:
        """
        self.scale = self.scale * scale # Store current scale for future use

        width = int(self.img.shape[1] * scale)
        height = int(self.img.shape[0] * scale)

        self.img = cv2.resize(self.img, (width, height), interpolation=cv2.INTER_AREA)

    def scale_x_y(self, x, y):
        return int(self.scale * (y+.5)), int(self.scale * (x+.5))

    def text(self, x, y, color, text):
        loc = (y * self.scale - 8, x * self.scale - 8)
        cv2.putText(self.img, str(text), loc, cv2.FONT_HERSHEY_SIMPLEX, 0.4, cv2_color[color], 1)

    def store(self, name: str):
        cv2.imwrite(str(storage / self.snap_name / f'{name}.png'), self.img)

    def show(self, pause=True):
        cv2.imshow(self.snap_name, self.img)
        if pause:
            cv2.waitKey(0)
            cv2.destroyWindow(self.snap_name)

    def line_mx_c(self, m: float, c: float, color: str):
        """
        Show line Y = mX + c
        If Coefficient m and c are given, the line will be drawn
        :param m:
        :param c:
        :param color:
        :return:
        """
        first = (0, int(c))
        second = (IMAGE[0], int(IMAGE[0] * m + c))
        self.draw_line(first, second, color)

    def draw_line(self, start: Tuple[int, int], end: Tuple[int, int], color, width=1):
        """
        Draw a strait line between 2 coordinates
        :param start: (x, y)
        :param end: (x, y)
        :param color:
        :param width:
        :return:
        """
        first = (start[1] * self.scale, start[0] * self.scale)
        second = (end[1] * self.scale, end[0] * self.scale)
        cv2.line(self.img, first, second, cv2_color[color], width)


if __name__ == "__main__":
    plot = DataPlot('lantaarn')
    plot.rescale(2)
    plot.show()

