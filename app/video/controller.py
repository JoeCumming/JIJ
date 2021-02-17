from flask import Blueprint, jsonify, abort, request, make_response, url_for, send_file, render_template, current_app
from os.path import basename, join

#from app.auth import auth
from lib.video.compositor import CompositeVideoCreator

video = Blueprint('video', __name__, url_prefix="video", template_folder="templates")
compositor = CompositeVideoCreator()

@video.route('/')
def index():
    return render_template("video.html")


#@video.route('/compose', methods = ['POST'])
#@auth.login_required
#def create_task():
#    if not request.json or not 'candidate_url' in request.json:
#        abort(400)

#    url = request.json['candidate_url']
#    compositor = CompositeVideoCreator()
#    outfile = compositor.createCompositeInteview(url)   
#    return jsonify( {'output': outfile } ), 201


@video.route('/compose', methods = ['POST'])
#@auth.login_required
def create_composite():
    if not request.form or not 'candidate_url' in request.form:
        abort(400)

    try:
        url = request.form['candidate_url']               
        outpath = join(current_app.root_path, 'static', 'video')    
        outfile = compositor.createCompositeInteview(url, outpath)   
        return send_file(outfile, attachment_filename=basename(outfile), as_attachment=True), 201
    except Exception as e:
        return str(e), 500