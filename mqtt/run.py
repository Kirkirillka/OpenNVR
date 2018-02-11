import paho.mqtt.client as paho
import os,datetime,random,hashlib
from binascii import hexlify


client=paho.Client()


def on_connect(client,userdata,flags,rc):
    print("CONNACK received with code %d."%(rc))

def on_publish(client,userdata,mid):
    print("mid:"+str(mid))


id=os.environ.get('MQTT_CLIENT_ID')
if not id:
    data=os.environ.get('HOSTNAME','')+datetime.datetime.now().strftime("%a %d %b%Y %H:%M:%S")+str(random.randint(0,1024))
    id=hexlify(hashlib.sha256(data.encode()).digest()).decode()[:50]
    os.environ['MQTT_CLIENT_ID']=id

print("ID:",id)

client.on_connect=on_connect
client.on_publish=on_publish
client.connect("localhost",1883)
client.loop_forever()