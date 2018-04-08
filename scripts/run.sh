#!/bin/bash

if [ $# -ne 3 ];then
	echo -e "Using:$0 {source} {stream_port} {mode}"
	exit 1
fi


#Name of source
SOURCENAME=$1
STREAM_PORT=$2
MODE=$3

echo $MODE

if [ ! -c $SOURCENAME ]; then
	echo -e "Video source doesn't exist on the system."
	echo -e "Please, check connection from your camera to USB-port."
	exit 2
fi

#Need to create a path to a dictionary you use to store video on
STORE_PATH="/var/opt/py_cam/backup"
STORE_NAME="output-%03d.mp4"

#If upload folder is not exist then create it
if [ ! -d  "$STORE_PATH/$SOURCENAME" ];then
	mkdir -p "$STORE_PATH/$SOURCENAME"
fi

#https://www.ffmpeg.org/ffmpeg-formats.html#segment_002c-stream_005fsegment_002c-ssegment

#How many times between two segments
SEGMENT_TIME=2
#How to store fragments
SEGMENT_FORMAT="mp4"
#There is a list to restore original videoline
SEGMENT_LIST="$STORE_PATH/$SOURCENAME/frag_list.m3u8"
#How many segments to store
LIMIT=10

if [ "$MODE" == "BACKUP" ]; then

	echo backup is on

	ffmpeg -f v4l2 -i $SOURCENAME  -f mpegts -codec:v mpeg1video -s 320x240 -b:v 1000k -bf 0 -codec:a mp2 -b:a 128k -muxdelay 0.001 http://0.0.0.0:$STREAM_PORT/flow \
	\-s 320x240 -f segment -segment_list $SEGMENT_LIST -segment_list_size $LIMIT -segment_wrap $LIMIT -segment_time $SEGMENT_TIME -segment_format $SEGMENT_FORMAT "$STORE_PATH/$SOURCENAME/$STORE_NAME"
	exit 0
fi

if [ "$MODE" == "BASIC" ];then

	ffmpeg -f v4l2 -i /dev/video0  -f mpegts -codec:v mpeg1video -s 320x240 -b:v 1000k -bf 0 -codec:a mp2 -b:a 128k -muxdelay 0.001 http://0.0.0.0:$STREAM_PORT/flow
	exit 0
fi

echo -e "Warning!"
echo -e "There are no necessary env variablies to supply information for streaming script."
echo -e "Check source code to examine if your system configured properly."
