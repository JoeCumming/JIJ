import os
from flask import Flask
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

from app.worker import FlaskCelery
from config import config, Config

#from sqlalchemy import create_engine
#from sqlalchemy.orm import sessionmaker

#engine = create_engine(app.config.get('SQLALCHEMY_DATABASE_URI'))
#dbsession = scoped_session(sessionmaker(bind=engine))


from lib.db import db

socketio = SocketIO()
celery = FlaskCelery(__name__, broker=Config.CELERY_BROKER_URL)


def create_app(config_name): 

    app = Flask(__name__, static_url_path = "", instance_relative_config=True)
    app.config.from_object(config[config_name])

    db.init_app(app)
    socketio.init_app(app, host='0.0.0.0', message_queue=Config.CELERY_BROKER_URL)
    celery.conf.update(app.config)

    from app.main.controller import main
    app.register_blueprint(main, url_prefix='/')

    from app.video.controller import video
    app.register_blueprint(video, url_prefix='/video')

    return app

