from flask import Blueprint, jsonify, abort, request, make_response, render_template

from service.auth import auth
from lib.video.compositor import CompositeVideoCreator

video = Blueprint('video', __name__, url_prefix="video", template_folder="templates")

@video.route('/')
def index():
    return render_template("video.html")


@video.route('/compose', methods = ['POST'])
#@auth.login_required
def create_task():
    if not request.json or not 'candidate_url' in request.json:
        abort(400)

    url = request.json['candidate_url']
    compositor = CompositeVideoCreator()
    outfile = compositor.createCompositeInteview(url)   
    return jsonify( {'output': outfile } ), 201
