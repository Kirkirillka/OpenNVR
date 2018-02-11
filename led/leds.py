from led.utils import ON_ERROR, ON_SUCCESS


from led.utils import UnixBroker

class Broker(UnixBroker):

    def __init__(self):
        super(Broker, self).__init__()

    def show_error(self):
        self.send(ON_ERROR)

    def show_success(self):
        self.send(ON_SUCCESS)