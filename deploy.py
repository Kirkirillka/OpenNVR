import os
import sys
import json

if os.getuid()!=0:
    print("Must be run as root.")
    exit()

stream_service_template= """
[Unit]
Description=OpenDVP ffmpeg stream flow {i} service
StopWhenUnneeded=true


[Service]
Type=simple
ExecStart=/bin/bash -c "ffmpeg -f v4l2 -i {source} -f alsa -ar 44100 -i hw:0 -f mpegts -codec:v mpeg1video -s 320x240 -b:v 1000k -bf 0 -codec:a mp2 -b:a 128k -muxdelay 0.001  http://0.0.0.0:{stream_port}/flow"
Restart=always
RestartSec=5
StartLimitInterval=10
StartLimitBurst=3


[Install]
WantedBy=multi-user.target
"""

cam_service_template="""
[Unit]
Description=OpenDVP cam {i} service
StopWhenUnneeded=true


[Service]
Type=simple
WorkingDirectory={directory}
ExecStart=/bin/bash -c "python3.6 streamer.py {source} --port {stream_port} --ws_port {ws_port}"
Restart=always
RestartSec=5
StartLimitInterval=10
StartLimitBurst=3



[Install]
WantedBy=multi-user.target
"""


web_service_template="""
[Unit]
Description=OpenDVP Web broker service
StopWhenUnneeded=true


[Service]
Type=simple
WorkingDirectory={directory}
ExecStart=/bin/bash -c "python3.6 web_broker.py"
RestartSec=5
StartLimitInterval=10
StartLimitBurst=3
Restart=always

[Install]
WantedBy=multi-user.target
"""


led_service_template="""
[Unit]
Description=OpenDVP LED broker service
StopWhenUnneeded=true

[Service]
Type=simple
WorkingDirectory={directory}
ExecStart=/bin/bash -c "python3 unix_run.py"
Restart=always
RestartSec=5
StartLimitInterval=10
StartLimitBurst=3

[Install]
WantedBy=multi-user.target
"""

pydvr_target_template="""
[Unit]
Description=OpenDVR target
{}
Wants=pyledbroker.service web.service
After=multi-user.target
AllowIsolate=yes
Restart=always
RestartSec=5
StartLimitInterval=10
StartLimitBurst=3
"""

cams=json.load(open("config"))

print("...Start adding services for webcam flow from the config file")

for cam in cams['SOURCES']:
    i=cams['SOURCES'][cam]["id"]
    source=cams['SOURCES'][cam]["source"]
    ws_port=cams['SOURCES'][cam]["ws_port"]
    stream_port=cams['SOURCES'][cam]['stream_port']

    with open("/etc/systemd/system/pyffmpeg{}.service".format(i), "w") as service:
        service.write(stream_service_template.format(i=i, source=source, stream_port=stream_port))

    print("\t...Done with <pyffmpeg{i}> cam on {source}:{stream_port} source".format(i=i, source=source, stream_port=stream_port))


print("...Start adding services for py cams from the config file")

for cam in cams['SOURCES']:
    i=cams['SOURCES'][cam]["id"]
    source=cams['SOURCES'][cam]["source"]
    ws_port=cams['SOURCES'][cam]["ws_port"]
    stream_port=cams['SOURCES'][cam]['stream_port']

    with open("/etc/systemd/system/pycam{}.service".format(i),"w") as service:
        pwd=os.path.abspath(os.curdir)+'/cam'
        service.write(cam_service_template.format(i=i,
                                                directory=pwd,
                                                source=source,
                                                stream_port=stream_port,
                                                ws_port=ws_port
                                                 )
                    )

    print("\t...Done with <pycam{}> cam on {}:{} source".format(i,source,stream_port))

print("...Add web broker service")
with open("/etc/systemd/system/pywebbroker.service", "w") as service:
    pwd = os.path.abspath(os.curdir) + '/web'
    service.write(web_service_template.format(directory=pwd))

print("...Add LED broker service")
with open("/etc/systemd/system/pyledbroker.service", "w") as service:
    pwd = os.path.abspath(os.curdir) + '/led'
    service.write(led_service_template.format(directory=pwd))


print("...Add pyDVR target")

requires=["Requires=pycam{i}.service pyffmpeg{i}.service".format(i=i) for i in range(len(cams["SOURCES"]))]
with open("/etc/systemd/system/pydvr.target", "w") as target:
    target.write(pydvr_target_template.format('\n'.join(requires)))

print("Now run as root:\n\tsystemctl daemon-reload\n\tsystem enable pydvr.target")
