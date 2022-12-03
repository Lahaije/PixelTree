from machine import Pin
import neopixel
import sys
import json

"""
This file should be installed on a esp32 running micropython. 
"""

n = 50  # Number of connected Neopixels
p = 5  # Pin number connected to Neopixels

np = neopixel.NeoPixel(Pin(p), n)

np[0] = (255, 255, 255)
np[49] = (255, 255, 255)
np.write()


def main():
    led = Pin(2, Pin.OUT)
    enabled = False
    while True:
        if enabled:
            led.off()
        else:
            led.on()
        enabled = not enabled

        try:
            for line in sys.stdin:
                data = json.loads(line)
                counter = 0
                for rgb in data['rgb']:
                    np[counter] = (rgb['g'], rgb['r'], rgb['b'])
                    counter += 1
                np.write()
                print('done')
        except Exception as e:
            print(f"ERROR {e}")


if __name__ == '__main__':
    main()
