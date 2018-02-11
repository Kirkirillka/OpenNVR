import sys
import os

sys.path.insert(0, os.path.abspath("../"))
sys.path.insert(0, os.path.abspath("."))

from flask import Flask, send_from_directory, render_template, jsonify, request, redirect, url_for, Response, \
    get_flashed_messages, flash
from flask_security import login_required, current_user, roles_required, Security, SQLAlchemySessionUserDatastore
from flask_security.utils import hash_password


from web.auth.database import db_session, init_db
from web.auth.models import User, Role
from led import Broker
from web.utils import *
# from web.auth.database import init_security, hash_password

# from web.tasks import make_celery
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
# Initialize Celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

led = Broker()
services=ServiceBroker()

# Setup Flask-Security
user_datastore = SQLAlchemySessionUserDatastore(db_session,
                                                User, Role)
security = Security(app, user_datastore)



#Setup Flask-Redis for flashing messages :)
app.config['REDIS_URL']='redis://localhost:6379'
queue=MessageQueue(app)


@app.before_first_request
def init_basic_users():
    init_db()
    if not user_datastore.find_user(email='admin'):
        a = user_datastore.create_user(email='admin', password=hash_password('password'))
        user = user_datastore.create_user(email='user', password=hash_password('password'))
        b = user_datastore.find_or_create_role(name='admin')
        c = user_datastore.find_or_create_role(name='user')

        user_datastore.add_role_to_user(a, b)
        user_datastore.add_role_to_user(a, c)
        user_datastore.add_role_to_user(user, c)

        db_session.commit()


@celery.task()
def addCam(source):
    if create_cam_service(source):
        return True
    return False


@celery.task()
def delCam(source):
    if delete_cam_service(source):
        return True
    return False


@celery.task()
def updateConf(data):
    update_conf(data)
    return True


@app.route("/")
def index():
    led.show_success()
    return render_template("index.html", current_user=current_user)


@app.route("/settings", methods=['GET'])
# @login_required
# @roles_required('admin')
def settings():
    return render_template('settings.html', current_user=current_user)


@app.route("/config/<action>", methods=['GET', 'POST'])
# @login_required
def config(action):
    if request.method == 'GET':

        if current_user.has_role('user'):
            if action == 'get':
                return jsonify(get_config())

        if True or current_user.has_role('admin'):
            if action == 'reinitialize':
                result = update_available_sources()
                if result:
                    return jsonify(REINITILAZE)
                else:
                    return jsonify(ERROR)

        return Response()

    if request.method == 'POST':
        if current_user.has_role('admin'):
            if action == 'update':
                data = request.json
                # updateConf.apply_async([data, ])
                result = update_conf(data)
                if result:
                    return jsonify(UPDATE_CONFIG)
                return jsonify(ERROR)
            return redirect(url_for('index'))


@app.route('/users/<action>', methods=['GET', 'POST'])
def users(action='get'):
    if request.method == 'GET':

        user_list = [{'name': 'Kirill', 'enabled': True}, {'name': 'Oleg', 'enabled': False},
                     {'name': 'Max', 'enabled': True}]

        if True or current_user.has_role('user'):
            if action == 'current':
                return jsonify({'email': current_user.email,
                                'roles': [role.name for role in current_user.roles]
                                })

        if True or current_user.has_role('admin'):
            if action == 'get':
                users = []
                for user in User.query.all():
                    users.append({'id': user.id,
                                  'email': user.email,
                                  'username': user.username,
                                  'roles': [role.name for role in user.roles],
                                  'is_enabled': user.is_active}
                                 )
                return jsonify(users)

    if request.method == 'POST':

        if current_user.has_role('admin'):
            if action == 'add':
                pass
            if action == 'update':
                pass


@app.route("/cam/<action>", methods=['GET', 'POST'])
# @login_required
def sources(action):
    if request.method == 'GET':
        if True or current_user.has_role('user'):
            flash('user')
            if action == 'all':
                return jsonify(get_available_sources())
            if action == 'free':
                return jsonify(get_free_sources())
            if action == 'enabled':
                return jsonify(get_enabled_sources())

    if request.method == 'POST':
        if current_user.has_role('admin'):
            if action == 'add':
                src = request.json
                # result = addCam.delay(src)
                result = create_cam_service(src)
                return jsonify(CAM_ADDED)
                # if result.wait():
                #    return jsonify(dict(success='True'))
            if action == 'del':
                src = request.json
                result = delete_cam_service(src['name'])
                return jsonify(CAM_DELETED)
                # result=delCam.delay(src['name'])
                # if result.wait():
                #    return jsonify(dict(success='True'))
                # return jsonify(dict(success='False'))




@app.route("/services/",methods=['GET',])
def service_list():
    return jsonify(get_config()['services'])

@app.route("/service/<action>",methods=['POST',])
def service_do(action):
    service_name = request.json['name']
    result='False'
    if action=='on':
            result=services.start(service_name)
    if action=='off':
            result=services.stop(service_name)
    return jsonify({'success':result})

@app.route('/message/<email>/',methods=['GET',])
def message(email):
    if request.method=='GET':
        if email=='1' or  current_user.is_authenticated:
            return jsonify(
                dict(
                    [(i,r) for i,r in  enumerate(queue.pop(current_user.email))
                     ]
                )
            )
        return jsonify([])




@app.route('/static/<path>')
def get_static(path):
    led.show_error()
    return send_from_directory('static', path)


if __name__ == '__main__':
    app.run('0.0.0.0', debug=True)
