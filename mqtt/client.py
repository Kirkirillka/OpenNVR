import paho.mqtt.client as paho
import os,random,hashlib
from binascii import hexlify

from time import sleep
from datetime import datetime

from typing import Tuple,List
from mqtt.mixins import WifiMixin,WebguiMixin,ActionMixin,CmdMixin
from mqtt.mixins import LogMixin as logger

from json import dump,load,dumps,loads

TOPICS=["start","stop","wifi"]

class MQTT_Client(WifiMixin,WebguiMixin,ActionMixin,CmdMixin):

    def __init__(self,address: tuple):
        self._init_params()
        self._guid_()
        self._client=paho.Client(self.params["MQTT_CLIENT_ID"],clean_session=False,transport='udp')
        #self._client.on_message=self._on_message
        self._client.on_subscribe=self._on_subscribe

        self.is_connected=self._connect_(address)
        self._subscribe()

        self.logins=dict(success=0,failure=0)

    def _subscribe(self):
        if not self.is_connected:
            return
        id=self.params["MQTT_CLIENT_ID"]
        print(id)
        self._client.subscribe("rpi_cam/{}/wifi/".format(id))
        self._client.subscribe("rpi_cam/{}/webgui/".format(id))
        self._client.subscribe("rpi_cam/{}/cmd/".format(id))

        self._client.message_callback_add("rpi_cam/{}/wifi/".format(id), self.on_wifi)
        self._client.message_callback_add("rpi_cam/{}/webgui/".format(id), self.on_webgui)
        self._client.message_callback_add("rpi_cam/{}/cmd/".format(id), self.on_exec)

    def _init_params(self):
        with open("config","r") as file:
            params=load(file)
            if not len(params):
                self.params={}
            else:
                self.params=params

    def _dump_params(self):
        with open("config", "w") as file:
            dump(self.params,file)

    def _guid_(self):
            if not "MQTT_CLIENT_ID" in self.params:
                data = os.environ.get('HOSTNAME', '') + datetime.now().strftime("%a %d %b%Y %H:%M:%S") + str(
                    random.randint(0, 1024))
                id = hexlify(hashlib.sha256(data.encode()).digest()).decode()[:50]
                self.params["MQTT_CLIENT_ID"] = id
            else:
                id=self.params["MQTT_CLIENT_ID"]
            self.id=id
            self._dump_params()

    def _on_subscribe(self,client,userdata,mid,granted_qos):
        print("Subscribed: {} {}".format(client,granted_qos))


    def on_exec(self, client, userdata, msg):
        command = msg.payload.decode()
        res = self.execute(command)
        payload = dict(action="CmdExec",result=res, time=datetime.now().strftime("%d-%m-%Y %H:%M"))
        self._client.publish("rpi_cam/{}/cmd/result".format(self.id,command),dumps(payload))

    def _connect_(self,address:tuple) -> bool:
        try:
            self._client.connect(*address)
            return True
        except:
            return False


    def on_move(self):

        payload=dict(action="MoveDetect",move=True,time=datetime.now().strftime("%d-%m-%Y %H:%M"))
        self._client.publish("rpi_cam/{}/action/move".format(self.id),dumps(payload))
        super(MQTT_Client, self).on_move()

    def on_login(self,result:bool):
        if result:
            self.logins['success']+=1
        else:
            self.logins['failure']+=1
        payload=dict(action="LoginAttempt",result=result,time=datetime.now().strftime("%d-%m-%Y %H:%M"))
        self._client.publish("rpi_cam/{}/action/login".format(self.id),dumps(payload))
        self._client.publish("rpi_cam/{}/action/login/count".format(self.id), dumps(self.logins))
        super(MQTT_Client, self).on_login(result)

    def on_command(self,result):
        payload = dict(action="CmdExec",result=result,time=datetime.now().strftime("%d-%m-%Y %H:%M"))
        self._client.publish("rpi_cam/{}/cmd/".format(self.id), dumps(payload))
        super(MQTT_Client, self).on_command(result)

    def serve(self,loop=False)->None:
        if loop:
            self._client.loop_forever()
        self._client.loop_start()

if __name__ == '__main__':
    client=MQTT_Client(("localhost",1883))
    client.serve()
    client.on_move()
    client.on_login(False)
    client.on_command(False)
    while 1:pass