from flask import Blueprint, jsonify, abort, request, make_response, url_for, send_file, render_template, current_app, redirect
from flask.config import Config
from flask_socketio import SocketIO
#from concurrent.futures import ThreadPoolExecutor

import os
import logging


#from app.auth import auth

from lib.db import db
from lib.db.models import Video
from lib.video.creator import VideoCreator
from app.worker.tasks import create_video

#executor = ThreadPoolExecutor(2)

video = Blueprint('video', __name__, url_prefix="video")


@video.route('/')
def index():
    try:             
        return render_template("video/videos.html", videos=Video.query.all())
    except Exception as e:
        return str(e), 500    


@video.route('/request')
#@auth.login_required
def request_composite():
    try:
        return render_template("video/video_request.html")
    except Exception as e:
        return str(e), 500    


@video.route('/download/<id>')
#@auth.login_required
def download(id):
    if not id:
        abort(400)

    try:
        video = join(current_app.root_path, 'static', 'video', id)            
        return send_file(video, attachment_filename=basename(id), as_attachment=True), 201
    except Exception as e:
        return str(e), 500


@video.route('/delete/<id>')
#@auth.login_required
def delete(id):
    if not id:
        abort(400)
        
    try:        
        record = Video.query.get(id)
        if os.path.exists(record.composite_url):
            os.remove(record.composite_url)
        db.session.delete(record)
        return redirect(url_for('video.index'))
    except Exception as e:
        return str(e), 500
    finally:
        db.session.commit()


@video.route('/compose', methods = ['POST'])
#@auth.login_required
def compose():
    if not request.form or not 'candidate_url' in request.form :
        abort(400)
    
    try:                                                     
        video = Video(name="pending...", jij_url=request.form['candidate_url'])
        db.session.add(video)
        db.session.commit()
        
        task = create_video.delay(video.id, current_app.root_path)        
        return redirect(url_for('video.index'))
    except Exception as e:
        return str(e), 500
    finally:
        db.session.commit()


#def create_composite(creator: VideoCreator):  
#    try:                                              
#        creator.createAndUpload()        
#        #creator.appcontext.status('Finished')
#    except Exception as e:
#        logging.exception(e)
#        creator.video.error = True
#        creator.video.status = 'Error : ' + str(e)
#        #creator.appcontext.db.session.commit()  
#    finally:        
#        #creator.appcontext.emit('complete')
#        pass
