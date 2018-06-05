#!/usr/bin/env bash

#Arguments to substitute
ACTION=$1
NAME=$2
SOURCE=$3
DIRECTORY="/opt/opennvr/cam"
WS=$4
HTTP=$5
MODE=$6
SIZE=$7

echo $DIRECTORY >/tmp/echo

#Temporary files location before copy to Systemctl directory
TMP_CAM=/tmp/cam
TMP_FFMPEG=/tmp/ffmpeg

SERVICE_DIR=/etc/systemd/system/
TEMPLATES_DIR=/var/opt/opennvr/service_templates

#Constants
CAM_PREFIX_NAME='py_'
FFMPEG_PREFIX_NAME='pyff_'

if [[ $ACTION == 'delete' ]];then
        if [ $# != 2 ];
            then
                echo 'Need exacly one extra args for delete: , NAME'
                exit 1
            fi
        #Creating path to services
        CAM_PATH=$SERVICE_DIR$CAM_PREFIX_NAME$NAME.service
        FFMPEG_PATH=$SERVICE_DIR$FFMPEG_PREFIX_NAME$NAME.service

        #Stop services
        systemctl stop $CAM_PREFIX_NAME$NAME
        systemctl stop $FFMPEG_PREFIX_NAME$NAME

        #Delete services
        #Check if cam exist
        if [ -f  $CAM_PATH ]; then
            rm $CAM_PATH
        fi

        #check if ffmpeg exist
        if [ -f  $FFMPEG_PATH ]; then
            rm $FFMPEG_PATH
        fi

        #Reload daemons
        systemctl daemon-reload

        echo "It' s successfully done!"
        exit 0
    fi


if [  $# != 7 ]
    then
        echo "Need exacly six extra  args to create:  NAME, SOURCE, WEBSOCKET_PORT, HTTP_PORT, MODE, VIDEOSIZE"
        exit 1
fi



if [[ $ACTION == 'create' ]];then

        #Creating pycam service in TMP
        cat $TEMPLATES_DIR/pycam.template | sed -e "s|{i}|$SOURCE|g" | sed -e "s|{directory}|$DIRECTORY|g" | sed -e "s|{source}|$SOURCE|g"| sed -e "s|{stream_port}|$HTTP|g" | sed -e "s|{ws_port}|$WS|g" > $TMP_CAM

        #Creating pyffmpeg service in TMP
        cat $TEMPLATES_DIR/pyffmpeg.template | sed -e "s|{videosize}|$SIZE|g" | sed -e "s|{i}|$SOURCE|g" | sed -e "s|{directory}|$DIRECTORY|g" | sed -e "s|{source}|$SOURCE|g"| sed -e "s|{stream_port}|$HTTP|g" | sed -e "s|{ws_port}|$WS|g" | sed -e "s|{mode}|$MODE|g" > $TMP_FFMPEG

        #Creating path to services
        CAM_PATH=$SERVICE_DIR$CAM_PREFIX_NAME$NAME.service
        FFMPEG_PATH=$SERVICE_DIR$FFMPEG_PREFIX_NAME$NAME.service


        #Check if cam exist arleady
        if [ -f  $CAM_PATH ]; then
            exit 1
        fi

        #check if ffmpeg exist already
        if [ -f  $FFMPEG_PATH ]; then
            exit 1
        fi

        #Moving services from TMP to daemon directory
        cp $TMP_CAM $CAM_PATH
        cp $TMP_FFMPEG $FFMPEG_PATH

        #Enable to load on boot in
        systemctl enable $CAM_PREFIX_NAME$NAME.service > /dev/null
        systemctl enable $FFMPEG_PREFIX_NAME$NAME.service > /dev/null
        systemctl daemon-reload

        echo $CAM_PREFIX_NAME$NAME > /tmp/123

        #Start this
        systemctl start $CAM_PREFIX_NAME$NAME
        systemctl start $FFMPEG_PREFIX_NAME$NAME


        #It's successfully done
        echo "It' s successfully done!"
        exit 0
fi