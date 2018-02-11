import glob
import subprocess
import os
from json import dumps, loads, dump, load

from flask_redis import FlaskRedis

from itertools import count

CAM_DIR = '/home/bachelor/Desktop/py_cam/cam/'
FFMPEG_DIR = ''

enabled_sources = []
available_sources = []


WEB_CONF_PATH = 'web_config/web.conf'



def dict_equal(dict_a, dict_b):
    if len(set(dict_a.keys()) - set(dict_b.keys())) == 0:
        if len(set(dict_a.values()) - set(dict_b.values())) == 0:
            return True
    return False


def dict_in(foo, sequence):
    return any([dict_equal(foo, a) for a in sequence])


class ConfigManager():

    def update(self,data):
        fields = ['width', 'height', 'message']
        config = load(open(WEB_CONF_PATH))
        for r in data:
            if r in fields:
                config[r] = data[r]
        dump(config, open(WEB_CONF_PATH, 'w'))
        return True

    @property
    def hive(self):
        return load(open(WEB_CONF_PATH))



class SourceManager():

    ENABLED_SOURCES_PATH = 'web_config/en_sources.json'
    ALL_SOURCES_PATH = 'web_config/all_sources.json'

    def __init__(self):
        pass

    def __scan(self, ws_start_port=8060, http_start_port=8061, ws_step=2, http_step=2):
        source_dict = []
        ws_seq = count(ws_start_port, ws_step)
        http_seq = count(http_start_port, step=http_step)
        for index, source in enumerate(glob.iglob('/dev/video*')):
            foo = {'name': index,
                   'source': source,
                   'ws_port': next(ws_seq),
                   'http_port': next(http_seq)
                   }
            source_dict.append(foo)
        return source_dict

    @property
    def availiable(self):
        with open(self.ALL_SOURCES_PATH) as file:
            return load(file)

    @property
    def enabled(self):
        try:
            data = load(open(self.ENABLED_SOURCES_PATH))
        except:
            data = []
        return data

    @property
    def free(self):
        all_sources = self.availiable
        en_sources = self.enabled

        out = []

        for source in all_sources:
            is_free = True
            for en_src in en_sources:
                if dict_equal(source, en_src):
                    is_free = False
                    break
            if is_free: out.append(source)

        return out

    def __connect(self, source):
        try:
            current_en_sources = self.enabled
            if len(current_en_sources) == 1:
                current_en_sources = list(current_en_sources)
        except:
            current_en_sources = []

        free_sources = self.free()

        if dict_in(source, free_sources):
            current_en_sources.append(source)
            with open(self.ENABLED_SOURCES_PATH, 'w') as file:
                dump(current_en_sources, file)
            return True
        else:
            return False

    def update_db(self):
        all_sources = self.__scan()
        with open(self.ALL_SOURCES_PATH, 'w') as file:
            dump(all_sources, file)
        return True


    def add_cam(self,source):
        if isinstance(source, str):
            src = loads(source)
        else:
            src = source

        if not 'name' in src or \
                not 'source' in src or \
                not 'ws_port' in src or \
                not 'http_port' in src: \
                raise AttributeError('Not enough data in supplied JSON to create service')

        name = str(src['name'])
        source = str(src['source'])
        ws_port = str(src['ws_port'])
        http_port = str(src['http_port'])
        result = self.__connect(src)

        if result:
            p = subprocess.check_call(
                ['/home/bachelor/Desktop/py_cam/web/cam_builder.sh', 'create', name, source, CAM_DIR, ws_port,
                 http_port],
            )
            # print(p.communicate())
            return True
        return False

    def del_cam(self,source):
        enabled_sources = self.enabled
        sources = list(enumerate([r['name'] for r in enabled_sources]))
        for index, cam in sources:
            if str(cam) == str(source):
                deleted = enabled_sources.pop(index)

                dump(enabled_sources, open(self.ENABLED_SOURCES_PATH, 'w'))

                p = subprocess.check_call(
                    ['/home/bachelor/Desktop/py_cam/web/cam_builder.sh', 'delete', str(source)],
                )
                # print(p.communicate())

                self.update_db()

                return True
        return False



class MessageQueue():

    def __init__(self, app):
        self.redis_store = FlaskRedis(app)

    def push(self, user_id, message):
        self.redis_store.lpush(user_id, message)
        return True

    def pop(self, user_id, **args):
        while True:
            data = self.redis_store.rpop(user_id)
            if data:
                yield data.decode()
            else:
                return

class ServiceBroker():
    def __init__(self):
        self.allowed_services = ['ssh', 'ftp']
        pass

    def start(self, service):
        if not service in self.allowed_services:
            return False
        config = load(open(WEB_CONF_PATH))
        subprocess.check_call(['systemctl enable ' + service, ], shell=True)
        subprocess.check_call(['systemctl start ' + service, ], shell=True)
        config['services'][service] = 'on'
        dump(config, open(WEB_CONF_PATH, 'w'))
        return True

    def stop(self, service):
        if not service in self.allowed_services:
            return False
        config = load(open(WEB_CONF_PATH))
        subprocess.check_call(['systemctl disable ' + service, ], shell=True)
        subprocess.check_call(['systemctl stop ' + service, ], shell=True)
        config['services'][service] = 'off'
        dump(config, open(WEB_CONF_PATH, 'w'))
        return True

if __name__ == '__main__':
    src = '{"name":"test","source": "/dev/sda13", "ws_port": 8060, "http_port": 8061}'

    cam=SourceManager()
    cam.update_db()
    print(cam.free)
    print(cam.enabled)
    print(cam.availiable)
    cam.del_cam(cam.availiable[0]['name'])


    serv = ServiceBroker()
    serv.start('ssh')
    serv.stop('ssh')

    serv.start('ftp')
    serv.stop('ftp')

    serv.start('www')
    serv.stop('www')
