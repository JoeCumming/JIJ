from flask import Flask, make_response, jsonify

from app.main.controller import main
from app.video.controller import video

app = Flask(__name__, static_url_path = "", instance_relative_config=True)
app.config.from_object('config')
app.config.from_envvar('TARGET_ENV', silent=True)

@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify( { 'error': 'Bad request' } ), 400)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify( { 'error': 'Not found' } ), 404)      


app.register_blueprint(main, url_prefix='/')
app.register_blueprint(video, url_prefix='/video')
