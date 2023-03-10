print('main')
from programs import run
import uasyncio as asyncio

from web_page import serve

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(run())
    loop.create_task(asyncio.start_server(serve, "0.0.0.0", 80))

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("closing")
        loop.close()
    except Exception as e:
        print(e)
