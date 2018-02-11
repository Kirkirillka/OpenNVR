import asyncio

from time import sleep

from led.utils import LED
#from gpiozero import LED as LED

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