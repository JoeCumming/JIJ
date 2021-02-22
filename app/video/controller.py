from flask import Blueprint, jsonify, abort, request, make_response, url_for, send_file, render_template, current_app, redirect
from flask_socketio import SocketIO
from concurrent.futures import ThreadPoolExecutor
from os import listdir, remove
from os.path import basename, join, isfile, getsize, getctime
import time
import logging

from youtube_video_upload import upload_from_options
import youtube_video_upload

#from app.auth import auth

from lib.db import db
from lib.db.models import Video

from lib.video.compositor import CompositeVideoCreator
from lib.video.options import VideoDescriptor, LoadDescriptor


video = Blueprint('video', __name__, url_prefix="video", template_folder="templates")

compositor = CompositeVideoCreator()
executor = ThreadPoolExecutor(2)


@video.route('/')
def index():
    try:             
        return render_template("videos.html", videos=Video.query.all())
    except Exception as e:
        return str(e), 500    


@video.route('/request')
#@auth.login_required
def request_composite():
    return render_template("video_request.html", categories = youtube_video_upload.get_category_number.IDS )


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
        remove(join(current_app.root_path, 'static', 'video', id))
        return redirect(url_for('video.index'))
    except Exception as e:
        return str(e), 500


@video.route('/compose', methods = ['POST'])
#@auth.login_required
def compose():
    if not request.form or not 'candidate_url' in request.form :
        abort(400)

    if 'load' in request.form and request.form['load'] == 'on' and not 'title' in request.form :
        abort(400, "The video needs a title to upload")
            
    try:    
        
        url = request.form['candidate_url']     
        base = "{}.mp4".format(basename(url))
        title = request.form['title'] if 'title' in request.form else base
        privacy = 'unlisted'
        category = 'Education'

        #dbrecord = Video(jij_url=url)

        outpath = join(current_app.root_path, 'static', 'video', base) 
        loader = LoadDescriptor(current_app.config['SECRETS_FILE'], current_app.config['CREDENTIALS_FILE'], True)      
        loader.add_video(VideoDescriptor(title, outpath, "This is a test", privacy, category))          
        executor.submit(create_composite, url, loader, outpath, current_app.extensions['socketio'])
                
        return redirect(url_for('video.index'))
    except Exception as e:
        return str(e), 500



def create_composite(url, loader: LoadDescriptor, outpath: str, socket: SocketIO):  
    try:        
        compositor.createCompositeInteview(url, outpath)          
        socket.emit('status', {'msg':'Composite video is complete. Loading to YouTube...'}, namespace = '/events')

        link = upload_from_options(loader.asDictionary())
        socket.emit('status', {'msg':'YouTube load is complete'}, namespace = '/events')
    except Exception as e:
        logging.exception(e)

