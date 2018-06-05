import asyncio
from led.utils import module_exists
import importlib


from time import sleep

#Check if we can use GPIO. We just consider if system has that module it can use GPIO :)
if module_exists('gpiozero'):
    importlib.import_module('gpiozero','LED')
else:
    from led.utils import LED


from led.utils import STANDBY,SUCCESS,ERROR,ON_SUCCESS,ON_ERROR,TIMEOUT

class LED_ServerProtocol(asyncio.Protocol):
    standby = LED(STANDBY)
    error = LED(ERROR)
    success = LED(SUCCESS)
    standby.on()

    def data_received(self, data):
        led=LED_ServerProtocol.error
        if data == ON_SUCCESS:
            led = LED_ServerProtocol.success
        led.on()
        sleep(TIMEOUT)
        led.off()