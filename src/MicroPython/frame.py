from pixel import pixels


class Frames:
    def __init__(self, num):
        """
        hold an array of frame buffers.
        the Buffur first has a boolean. If True, the buffer is displayed and can be reused.
        If false, it is waiting to be displayed.

        :param num: number of frames
        """
        self.fps = 24
        self.num = num
        self.buffer = [bytearray(pixels.num_leds*3)] * num
        self.shown = [True] * num
        self.display = 0

    def store(self, frame) -> bool:
        """
        Store the frame in the first available buffer.
        Return False is all buffers are filled.
        :param frame:
        :return:
        """
        for i in range(self.num):
            num = i + self.display
            if num >= self.num:
                num -= self.num
            if self.shown[num]:
                self.buffer[num] = frame
                self.shown[num] = False
                return True

        return False

    def run_next(self):
        if self.shown[self.display]:
            return False

        for i in range(pixels.num_leds):
            data = self.buffer[self.display][3*i:3*i+3]
            pixels[i] = (data[1], data[0], data[2])
        pixels.show()

        self.shown[self.display] = True
        self.display += 1
        if self.display == self.num:
            self.display = 0

        return True


frames = Frames(10)
