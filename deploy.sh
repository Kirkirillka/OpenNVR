#!/bin/bash


#Create direcotry erarshy
#
#/var/opt/py_cam/scripts - where are scripts left
#/var/opt/py_cam/backups - where are backups left
#/var/opt/py_cam/service_templates - where are service templates left
#/opt/py_cam/cam - main flow server
#/opt/py_cam/web - webserver


mkdir -p /var/opt/py_cam/
mkdir -p /var/opt/py_cam/backups
mkdir -p /opt/py_cam/

cp -r scripts /var/opt/py_cam/
cp -r service_templates /var/opt/py_cam
cp -r cam /opt/py_cam/
cp -r web /opt/py_cam/
cp -r led /opt/py_cam
cp __init__.py /opt/py_cam

