import sys
import os

sys.path.insert(0, os.path.abspath("../"))
sys.path.insert(0, os.path.abspath("."))

from flask import Flask, send_from_directory, render_template, jsonify, request, redirect, url_for, Response, flash,abort
from flask_security import current_user, Security, SQLAlchemySessionUserDatastore,login_required,roles_required
from flask_security.utils import hash_password,verify_and_update_password,logout_user
from web.auth.database import db_session, init_db
from web.auth.models import User, Role
from led import Broker
from web.utils import ServiceManager,MessageQueue,SourceManager,ConfigManager,BackupManager
from celery import Celery
from web.notices import *



app = Flask(__name__)

app.config['SECRET_KEY'] = os.urandom(128)
app.config['SECURITY_PASSWORD_HASH'] = 'pbkdf2_sha512'
app.config['SECURITY_PASSWORD_SALT'] = b'12412126yyyg12t12125b125m125m21ffvdvsrbwenwey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///auth/users.db'

# Celery configuration
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379'
# Setup Flask-Redis for flashing messages :)
app.config['REDIS_URL']='redis://localhost:6379'
# Initialize Celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)


class UserManager():
    def __init__(self,app):
        # Setup Flask-Security
        user_datastore = SQLAlchemySessionUserDatastore(db_session,
                                                        User, Role)
        self._user_datastore=user_datastore
        self._security = Security(app, user_datastore)
        self._init_basic_users()


    def _init_basic_users(self):
        init_db()
        user_datastore=self._user_datastore
        if not user_datastore.find_user(email='admin'):
            a = user_datastore.create_user(email='admin', password=hash_password('password'))
            user = user_datastore.create_user(email='user', password=hash_password('password'))
            b = user_datastore.find_or_create_role(name='admin')
            c = user_datastore.find_or_create_role(name='user')

            user_datastore.add_role_to_user(a, b)
            user_datastore.add_role_to_user(a, c)
            user_datastore.add_role_to_user(user, c)

            db_session.commit()

    @property
    def users(self):
        _users=User.query.all()
        return [{'id': user.id,
                                  'email': user.email,
                                  'username': user.username,
                                  'roles': [role.name for role in user.roles],
                                  'is_enabled': user.is_active} for user in _users]

    @property
    def roles(self):
        _roles=['admin','user']
        return _roles

    @property
    def _update_fileds(self):
        _fields=['email','password','is_enabled','username']
        return _fields

    @property
    def fields(self):
        _fields = ['email', 'username', 'roles', 'is_enabled','password']
        return _fields


    def update(self,userid,data):

        #user=User.query.filter(User.id==userid).one_or_none()
        with app.app_context():
            _user=self._user_datastore.get_user(userid)
            #If there is no any Users with specific ID
            if not _user: return False
            #If there any other than allowed fields in data supplied
            #if  any([key not in self.fields for key in data.keys()]): return False
            for key,value in data.items():
                #Pass unnesessary fields
                if key  not in self._update_fileds:continue
                field=value
                if key=='password':
                    field=hash_password(value)
                if key=='is_enabled':
                    key='is_active'
                setattr(_user,key,field)
            #Commit changes
            db_session.commit()

        return True

    def add_user(self,user_data):

        with app.app_context():
            #If user exists
            if user_data['email'] in [r['email'] for r in self.users]:
                return 2

            # If there any other than allowed fields in data supplied
            if any([key not in self.fields for key in user_data.keys()]): return 1

            roles=user_data.get('roles',None)

            if not  roles or any([r not in self.roles for r in self.roles]):
                roles=['user',]

            hive=self._user_datastore
            _user=hive.create_user()

            for key,value in user_data.items():
                field=value
                if key=='password':
                    field = hash_password(value)
                setattr(_user,key,field)

            for role in roles:
                hive.add_role_to_user(_user,role)

            db_session.commit()

        return 0

    def del_user(self,userid):

        hive=self._user_datastore

        user=hive.find_user(id=userid)
        hive.delete_user(user)
        hive.commit()
        return 0

    def activate(self,userid):
        hive = self._user_datastore
        _user = hive.find_user(id=userid)
        if not _user: return False
        hive.activate_user(_user)
        hive.commit()
        return 0

    def deactivate(self,userid):
        hive = self._user_datastore
        _user = hive.find_user(id=userid)
        if not _user: return False
        hive.deactivate_user(_user)
        hive.commit()
        return 0

    def pwd_change(self,user,data):
        pwd=data.get('password')
        confirm=data.get('check')
        verified=verify_and_update_password(confirm,user)
        if verified:
            user.password=hash_password(pwd)
        return verified


queue=MessageQueue(app)
services=ServiceManager()
cam_server=SourceManager()
configurator=ConfigManager()
userManager=UserManager(app)
backupManager=BackupManager()
led = Broker()


@app.route("/")
def index():
    led.show_success()

    return render_template("index.html", current_user=current_user)


@app.route("/settings", methods=['GET'])
@login_required
@roles_required('admin')
def settings():
    led.show_success()
    if current_user.has_role('admin'):
        return render_template('settings.html', current_user=current_user)
    return redirect(url_for('index'))


@app.route("/config/<action>", methods=['GET', 'POST'])
@login_required
def config(action):
    if request.method == 'GET':

        if current_user.has_role('user'):
            if action == 'get':
                return jsonify(configurator.hive)

        if current_user.has_role('admin'):
            if action == 'reinitialize':
                result = cam_server.update_db()
                if result:
                    led.show_success()
                    return jsonify(REINITILAZE)
                else:
                    led.show_error()
                    return jsonify(ERROR)
        return Response()

    if request.method == 'POST':
        if current_user.has_role('admin'):
            if action == 'update':
                data = request.json
                result = configurator.update(data)
                if result:
                    led.show_success()
                    return jsonify(UPDATE_CONFIG)
                led.show_error()
                return jsonify(ERROR)
            return redirect(url_for('index'))


@app.route('/users/<action>', methods=['GET', 'POST'])
def users(action='get'):
    if request.method == 'GET':
        if current_user.has_role('user'):
            if action == 'current':
                led.show_success()
                return jsonify({'email': current_user.email,
                                'roles': [role.name for role in current_user.roles]
                                })

        if current_user.has_role('admin'):
            if action == 'get':
                led.show_success()
                return jsonify(userManager.users)
        led.show_error()
        return abort(401)

    if request.method == 'POST':
        if current_user.has_role('admin'):
            if action == 'add':
                data = request.json
                result = userManager.add_user(data)
                response = USER_ADD_FAILED
                if not result:
                    response = USER_ADD_SUCCESS
                    led.show_success()
                return jsonify(response)

            if action == 'del':
                data = request.json
                id = data['id']
                result = userManager.del_user(id)
                response = USER_DELETE_FAILED
                if not result:
                    response = USER_DELETE_SUCCESS
                    led.show_success()
                return jsonify(response)

            if action == 'update':
                update_data = request.json
                id = update_data.get('id',None)
                result = userManager.update(id,update_data)
                response = USER_UPDATE_FAILED
                if not result:
                    response = USER_UPDATE_SUCCESS
                    led.show_success()
                return jsonify(response)

            if action == 'pwd_change':
                update_data=request.form
                result = userManager.pwd_change(current_user, update_data)
                response = USER_PASSWORD_CHANGE_FAILED
                if result:
                    response = USER_PASSWORD_CHANGE_SUCCESS
                    led.show_success()
                    logout_user()
                return redirect(url_for('index'))

            if action == 'disable':
                data = request.json
                id = data['id']
                result = userManager.deactivate(id)
                response = USER_UPDATE_FAILED
                if not result:
                    led.show_success()
                    response = USER_UPDATE_SUCCESS
                return jsonify(response)

            if action == 'enable':
                data = request.json
                id = data['id']
                result = userManager.activate(id)
                response = USER_UPDATE_FAILED
                if not result:
                    led.show_success()
                    response = USER_UPDATE_SUCCESS
                return jsonify(response)

        return jsonify(ERROR)


@app.route("/cam/<action>", methods=['GET', 'POST'])
@login_required
def sources(action):
    if request.method == 'GET':
        if current_user.has_role('user'):
            flash('user')
            if action == 'all':
                led.show_success()
                return jsonify(cam_server.availiable)
            if action == 'free':
                led.show_success()
                return jsonify(cam_server.free)
            if action == 'enabled':
                led.show_success()
                return jsonify(cam_server.enabled)

    if request.method == 'POST':
        if current_user.has_role('admin'):
            if action == 'add':
                src = request.json
                led.show_success()
                result = cam_server.add_cam(src)
                return jsonify(CAM_ADDED)

            if action == 'del':
                src = request.json
                led.show_success()
                result = cam_server.del_cam(src['name'])
                return jsonify(CAM_DELETED)


            return jsonify(NO_ACTION)



@app.route("/services/",methods=['GET',])
def service_list():
    led.show_success()
    return jsonify(configurator.hive['services'])


@app.route("/services/restart",methods=['POST'])
def service_restart():
    result = services.restart()
    if result:
        led.show_success()
        return jsonify(SERVICE_RESTART_SUCCESS)
    led.show_error()
    return jsonify(SERVICE_RESTART_FAILED)



@app.route("/service",methods=['POST',])
def service_do():
    action = request.json['action']
    service_name = request.json['name']
    result='False'
    if action == 'on':
            led.show_success()
            result=services.start(service_name)
    if action == 'off':
            led.show_success()
            result=services.stop(service_name)
    return jsonify({'success':result})


@app.route('/message/<email>/',methods=['GET',])
def message(email):
    led.show_success()
    if request.method=='GET':
        if current_user.is_authenticated:
            led.show_success()
            return jsonify(dict([(i,r) for i,r in  enumerate(queue.pop(current_user.email))]))
        led.show_error()
        return jsonify([])


if __name__ == '__main__':
    app.run('0.0.0.0')
