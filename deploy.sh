#!/bin/bash


SERVICE_TEMPLATE=service_templates

#Create direcotry erarshy
#
#/var/opt/py_cam/scripts - where are scripts left
#/var/opt/py_cam/backups - where are backups left
#/var/opt/py_cam/service_templates - where are service templates left
#/opt/py_cam/cam - main flow server
#/opt/py_cam/web - webserver


if [[  "$1" == "install" ]];then

    #Extra libs
    apt-get install -f libpam0g-dev

    #Need to properly use pip for both python3.4 and python3.6
    easy_install-3.4 pip
    easy_install-3.6 pip

    pip3.6 install -r requirements.txt
    pip3.4 install -r requirements.txt

    #Extra packets
    apt-get install -f redis-server python-celery python3-celery celeryd uwsgi uwsgi-plugin-python3 ffmpeg


    ###--------------------------------------------------------------
    #Installing vsftpd daemon
    #apt-get install -f vsftpd
    cp vsftpd.conf /etc
    service vsftpd restart
    ###--------------------------------------------------------------




    ###--------------------------------------------------------------
    #Installing nginx server
    #Compiling nginx from sources with ngx_http_auth_pam_module

    #First try to install newest nginx and delete. Thus we keep directory hierarchy.
    apt-get install -f nginx
    apt-get remove -f nginx


    olddir=$(pwd)
    cd nginx/nginx-1.12.2
    echo $(pwd)
    #./configure --add-module=../ngx_http_auth_pam_module --without-http_rewrite_module
    #make
    #make install
    cd $olddir


    #Need for www-data nginx to be able to read from /etc/shadow for auth via nginx_pam_auth
    usermod -a -G shadow www-data

    cp py_cam /etc/nginx/sites-available
    rm /etc/nginx/sites-available/default
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




    ###-------------------------------------------------------------
    #Deploy systemd init scripts

    #Systemd services templates
    cp $SERVICE_TEMPLATE/opennvr.template /etc/systemd/system/opennvr.target
    cp $SERVICE_TEMPLATE/pyled.template /etc/systemd/system/pyled.service
    cp $SERVICE_TEMPLATE/pyweb.template /etc/systemd/system/pyweb.service
    #Enable all subsystems
    systemctl enable pyled
    systemctl enable pyweb
    systemctl enable opennvr.target

    #Update systemd current configuration
    systemctl daemon-reload
    # Force to reach out target
    systemctl start opennvr.target
    #Successfully done
    exit 0
fi


if [[ "$1" == "delete" ]];then

    #delete systemd services
    rm /etc/systemd/system/py* 2> /dev/null
    systemctl daemon-reload

    #Clean up directory structure
    rm -rf /var/opt/py_cam
    rm -rf /opt/py_cam
    rm -rf /var/www/py_cam

    #Delete nginx config for OpenNVR
    rm /etc/nginx/sites-available/py_cam
    rm /etc/nginx/sites-enabled/py_cam

    #Successfully done
    exit 0
fi

echo "Usage $0: $0 [install | delete]"
echo -e "$0 install - Install full OpenNVR system onto your computer."
echo -e "$0 delete - Clean up your system from all OpenNVR files."




