from json import dumps
from serial import Serial

from neopixel import NeoPixels


class SerialEsp:
    """
    Set up a serial connection to send and receive data.
    This class is set up to dump the NeaPixel data for all leds to a device running the micro python code
     as set up in the MicroPython module of this project.
    """

    def __init__(self, port: str = 'COM5', bautrate: int = 115200):
        self.port = port
        self.bautrate = bautrate

        self.ser = Serial(self.port, self.bautrate, timeout=1)

    def readline(self) -> str:
        return self.ser.readline().decode("utf-8").rstrip()

    def write(self) -> bool:
        """
        Write the NeoPixels to the esp.
        Return True if processed correctly
        :return:
        """
        self.ser.write(dumps(NeoPixels.json()).encode('utf-8'))
        self.ser.write(b'\n')
        return self.readline() == 'done'


esp = SerialEsp()

