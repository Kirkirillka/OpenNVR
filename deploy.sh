#!/bin/bash


#Create direcotry erarshy
#
#/var/opt/py_cam/scripts - where are scripts left
#/var/opt/py_cam/backups - where are backups left
#/var/opt/py_cam/service_templates - where are service templates left
#/opt/py_cam/cam - main flow server
#/opt/py_cam/web - webserver



#Extra libs
apt-get install -f libpam0g-dev



###--------------------------------------------------------------
#Installing vsftpd daemon
apt-get install -f vsftpd
cp vsftpd.conf /etc
service vsftpd restart
###--------------------------------------------------------------





###--------------------------------------------------------------
#Installing nginx server
#Compiling nginx from sources with ngx_http_auth_pam_module
olddir=$(pwd)
cd nginx/nginx-1.12.2
echo $(pwd)
./configure --add-module=../ngx_http_auth_pam_module --without-http_rewrite_module
#make
#make install
cd $olddir


#Need for www-data nginx to be able to read from /etc/shadow for auth via nginx_pam_auth
usermod -a -G shadow www-data

cp py_cam /etc/nginx/sites-available
ln -s /etc/nginx/sites-available/py_cam /etc/nginx/sites-enabled
service nginx restart
###--------------------------------------------------------------



###--------------------------------------------------------------
#Create PyCam specific directories
mkdir -p /var/opt/py_cam/
mkdir -p /var/opt/py_cam/backups
mkdir -p /opt/py_cam/
mkdir -p /var/www/py_cam

#Copy files
cp -r scripts /var/opt/py_cam/
cp -r service_templates /var/opt/py_cam
cp -r web/static /var/www/py_cam
cp -r cam /opt/py_cam/
cp -r web /opt/py_cam/
cp -r led /opt/py_cam
cp __init__.py /opt/py_cam
###--------------------------------------------------------------




