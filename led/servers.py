import sys
import os

sys.path.insert(0, os.path.abspath("../"))
sys.path.insert(0, os.path.abspath("."))

import asyncio

from time import sleep
from led.protocols import LED_ServerProtocol
from led.utils import UNIX_ADDRESS_SOCKET


class LED_TCPServer():
    def run(self, address, port):
        loop = asyncio.get_event_loop()
        coro = loop.create_server(LED_ServerProtocol, address, port)
        server = loop.run_until_complete(coro)
        loop.run_forever()
        loop.close()


class LED_UnixServer():
    def __init__(self):
        if os.path.exists(UNIX_ADDRESS_SOCKET):
            os.remove(UNIX_ADDRESS_SOCKET)

    def run(self):
        loop = asyncio.get_event_loop()
        coro = loop.create_unix_server(LED_ServerProtocol, UNIX_ADDRESS_SOCKET)
        server = loop.run_until_complete(coro)
        loop.run_forever()
        loop.close()
