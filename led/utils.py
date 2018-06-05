import socket
import tempfile
from pkgutil import iter_modules

STANDBY=17
ERROR=22
SUCCESS=27

ON_ERROR=b'0'
ON_SUCCESS=b'1'
TIMEOUT=0.1

UNIX_ADDRESS_SOCKET="/tmp/pyled.sock"
TCP_ADDRESS_SOCKET="localhost"
TCP_ADDRESS_PORT=1234


def get_temp_filepath():
    return "{}/{}".format("/tmp",next(tempfile._get_candidate_names()))


def module_exists(module_name):
    return  module_name in (name for loader,name,ispkg in iter_modules())

class LED():

    def __init__(self,definition):
        self.definition=definition
        print("Started")

    def on(self):
        print("ON! {}".format(self.definition))

    def off(self):
        print("OFF! {}".format(self.definition))


class UnixBroker():
    def __init__(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            self.sock.connect(UNIX_ADDRESS_SOCKET)
        except:
            pass
        self.stopped=False

    def send(self,data):
        def reconnect():
            try:
                self.sock.close()
                self.sock=socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                self.sock.connect(UNIX_ADDRESS_SOCKET)
                return True
            except:
                return False

        if self.stopped:return

        try:
            self.sock.send(data)
        except Exception as e:
            if not reconnect():
                self.stopped=True

class TcpBroker():
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((TCP_ADDRESS_SOCKET,TCP_ADDRESS_PORT))

class Broker(UnixBroker):

    def __init__(self):
        super(Broker, self).__init__()

    def show_error(self):
        self.send(ON_ERROR)

    def show_success(self):
        self.send(ON_SUCCESS)
