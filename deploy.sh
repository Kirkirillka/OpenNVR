#!/bin/bash


SERVICE_TEMPLATE=service_templates

#Create direcotry erarshy
#
#/var/opt/opennvr/scripts - where are scripts left
#/var/opt/opennvr/backups - where are backups left
#/var/opt/opennvr/service_templates - where are service templates left
#/opt/opennvr/cam - main flow server
#/opt/opennvr/web - webserver


if [[  "$1" == "install" ]];then

    #Extra libs
    apt-get install -f libpam0g-dev

    #Need to properly use pip for both python3.4 and python3.6
    easy_install-3.4 pip
    easy_install-3.6 pip

    pip3.6 install -r requirements.txt
    pip3.4 install -r requirements.txt

    #Extra packets
    apt-get install -f redis-server python-celery python3-celery celeryd uwsgi uwsgi-plugin-python3 ffmpeg openssl libssl-dev


    ###--------------------------------------------------------------
    #Installing vsftpd daemon
    apt-get install -f vsftpd
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


    cp py_web /etc/nginx/sites-available/
    rm /etc/nginx/sites-available/default
    ln -s /etc/nginx/sites-available/py_web /etc/nginx/sites-enabled


    #Generate SSL certificate
    #Disabled due to WebSocket SSL issue
#    openssl req -nodes -newkey rsa:4096 -keyout opennvr.key -out opennvr.csr -subj "/C=RU/ST=Tatarsten/L=Kazan/O=OpenNVR/OU=OpenNVR Development team/CN=opennvr.example.local"
#    openssl x509  -req -days 365 -in opennvr.csr -signkey opennvr.key -out opennvr.crt
#
#    rm opennvr.csr
#
#    mkdir -p /etc/ssl/certs/
#    mv opennvr.crt /etc/ssl/certs/
#
#    mkdir  -p /etc/ssl/private/
#    mv opennvr.key /etc/ssl/private/


    echo -e '127.0.0.1  opennvr.example.local' >> /etc/hosts
    service nginx restart
    ###--------------------------------------------------------------

    ###--------------------------------------------------------------
    #Create PyCam specific directories
    mkdir -p /var/opt/opennvr/
    mkdir -p /var/opt/opennvr/backups
    mkdir -p /opt/opennvr/
    mkdir -p /var/www/py_web

    #Copy files
    cp -r scripts /var/opt/opennvr/
    cp -r service_templates /var/opt/opennvr
    cp -r web/static /var/www/py_web
    cp -r cam /opt/opennvr/
    cp -r web /opt/opennvr/
    cp -r led /opt/opennvr
    cp __init__.py /opt/opennvr
    ###--------------------------------------------------------------


    ###-------------------------------------------------------------
    #Deploy systemd init scripts

    #Systemd services templates
    cp $SERVICE_TEMPLATE/opennvr.template /etc/systemd/system/opennvr.target
    cp $SERVICE_TEMPLATE/pyled.template /etc/systemd/system/pyled.service
    cp $SERVICE_TEMPLATE/pyweb.template /etc/systemd/system/pyweb.service

    #Need for www-data nginx to be able to read from /etc/shadow for auth via nginx_pam_auth
    usermod -a -G shadow www-data
    #Change ownerships
    chown -R www-data:www-data /opt/opennvr
    chown -R www-data:www-data /var/opt/opennvr

    #Enable all subsystems
    systemctl enable pyled
    systemctl enable pyweb
    systemctl enable opennvr.target

    #Update systemd current configuration
    systemctl daemon-reload

    #Check to restart subservices to rule them
    systemctl restart ssh
    systemctl restart ntp
    systemctl restart vsftpd

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
    rm -rf /var/opt/opennvr
    rm -rf /opt/opennvr
    rm -rf /var/www/opennvr

    #Delete nginx config for OpenNVR
    rm /etc/nginx/sites-available/py_web
    rm /etc/nginx/sites-enabled/py_web

    #Successfully done
    exit 0
fi

echo "Usage $0: $0 [install | delete]"
echo -e "$0 install - Install full OpenNVR system onto your computer."
echo -e "$0 delete - Clean up your system from all OpenNVR files."




