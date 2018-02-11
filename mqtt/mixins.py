from subprocess import Popen,PIPE
from json import loads

from db.utils import *

class WebguiMixin(object):


    def on_webgui_start(self):
        print("WEB-GUI has started")


    def on_webgui_stop(self):
        print("WEB-GUI has stoped")

    def on_webgui(self,client,userdata,msg):

        txt=msg.payload
        if txt==b'start':
            self.on_webgui_start()
        elif txt==b'stop':
            self.on_webgui_stop()



class CmdMixin(object):


    def execute(self,cmd):


        def is_json(my_json):
            try:
                json_object=loads(my_json)
            except:
                return False
            return True
        result=""
        if not is_json(cmd):
            result=Popen(cmd,shell=True,stdout=PIPE).stdout.read().decode()
        return result



class WifiMixin(object):




    def on_wifi(self,client,userdata,msg):

        @add_wifi_start
        def on_wifi_start():
            print("Wifi has started")

        @add_wifi_stop
        def on_wifi_stoped():
            print("Wifi has stoped")

        txt = msg.payload
        if txt == b'start':
            on_wifi_start()
        elif txt == b'stop':
            on_wifi_stoped()




class LogMixin(object):

    def log(self,func):
        func(self)
        print("logged")

class ActionMixin(object):

    @add_move_attempt
    def on_move(self):
        print("Moving")

    @add_login_attempt
    def on_login(self,result:bool):
        print("Logging")

    @add_exec_attempt
    def on_command(self,result):
        print("Commanding")