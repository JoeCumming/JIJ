import os
from flask import Flask
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

from app.worker import FlaskCelery
from config import config, Config
from lib.db import db, login

socketio = SocketIO()
celery = FlaskCelery(__name__, broker=Config.CELERY_BROKER_URL)

def create_db():
    db.create_all()

def create_app(config_name): 

    app = Flask(__name__, static_url_path = "", instance_relative_config=True)
    app.config.from_object(config[config_name])

    db.init_app(app)
    login.init_app(app)    
    login.login_view = 'auth.login'

    socketio.init_app(app, host='0.0.0.0', message_queue=Config.CELERY_BROKER_URL)
    celery.conf.update(app.config)

    from app.main.controller import main
    app.register_blueprint(main, url_prefix='/')

    from app.video.controller import video
    app.register_blueprint(video, url_prefix='/video')

    from app.auth.controller import auth
    app.register_blueprint(auth, url_prefix='/auth')

    app.before_first_request(create_db)   

    return app


