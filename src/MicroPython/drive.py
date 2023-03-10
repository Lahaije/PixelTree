import uasyncio as asyncio
import time
from pixel import pixels
import programs
from frame import frames


def direct(json):
    programs.CURR_PROG = 'pauze'
    i = 0
    for pix in json['frame']:
        r, g, b = pix
        if 0 <= r < 256 and 0 <= g < 256 and 0 <= b < 256:
            pixels[i] = (g, r, b)
        i += 1
        if i == pixels.num_leds:
            break

    pixels.show()


async def process_frame(frame):
    while not frames.store(frame):
        print(f"Waiting to store frame")
        await asyncio.sleep(0.1)


async def extract_config(data, reader):
    """
    Extract number of frames and fps send.
    :param data: data stream
    :param reader: server reader
    :return: (num_frames, fps, data)
    """

    if len(data) > 1:
        num_frames = int(data[0])
        fps = int(data[1])
        data = data[2:]
    elif len(data) == 1:
        num_frames = int(data[0])
        fps = int(await reader.read(1))
    else:
        d = await reader.read(2)
        num_frames = int(d[0])
        fps = int(d[1])
    return num_frames, fps, data


async def frame_stream(data, reader):
    programs.CURR_PROG = 'run_frame'

    num_frames, fps, data = await extract_config(data, reader)

    frames.fps = fps

    num_byte_in_frame = 3*pixels.num_leds
    processed_counter = 0

    timer = time.ticks_ms()
    while True:
        while len(data) >= num_byte_in_frame:
            await asyncio.sleep_ms(1)
            await process_frame(data[0:3*pixels.num_leds])
            processed_counter += 1
            data = data[3*pixels.num_leds:]

        if processed_counter == num_frames:
            break

        if time.ticks_diff(time.ticks_ms(), timer) > 5000:
            raise RuntimeError('Reading data took to long')
        data += await reader.read(num_byte_in_frame - len(data))
