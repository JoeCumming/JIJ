import os
from flask import Flask
from flask_socketio import SocketIO

from app.main.controller import main
from app.video.controller import video
from lib.db import db

app = Flask(__name__, static_url_path = "", instance_relative_config=True)
app.config.from_object('config.{}Config'.format(os.environ.get('APP_ENV', 'Dev')))

socketio = SocketIO()
socketio.init_app(app, host='0.0.0.0')
db.init_app(app)

app.register_blueprint(main, url_prefix='/')
app.register_blueprint(video, url_prefix='/video')
