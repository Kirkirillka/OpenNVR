from servers import LED_TCPServer
from utils import TCP_ADDRESS_SOCKET,TCP_ADDRESS_PORT


if __name__ == '__main__':
    server=LED_TCPServer()
    server.run(TCP_ADDRESS_SOCKET,TCP_ADDRESS_PORT)