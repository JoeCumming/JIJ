from flask import Blueprint, jsonify, abort, request, make_response, url_for, send_file, render_template, current_app, redirect
from concurrent.futures import ThreadPoolExecutor
from os import listdir, remove
from os.path import basename, join, isfile, getsize, getctime
import time
import logging

#from app.auth import auth
from lib.video.compositor import CompositeVideoCreator

video = Blueprint('video', __name__, url_prefix="video", template_folder="templates")
compositor = CompositeVideoCreator()
executor = ThreadPoolExecutor(2)

@video.route('/')
def index():
    try:                 
        outpath = join(current_app.root_path, 'static', 'video')    
        imgfiles = []
        for f in listdir(outpath):            
            imgfiles.append(FileDetails(f, getsize(join(outpath,f)), getctime(join(outpath,f))))

        imgfiles.sort(key=lambda x: x.ctime, reverse=True)
        return render_template("videos.html", videos=imgfiles)
    except Exception as e:
        return str(e), 500    


@video.route('/request')
#@auth.login_required
def request_composite():
    return render_template("video_request.html")

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
        video = join(current_app.root_path, 'static', 'video', id)            
        remove(video)
        return redirect(url_for('video.index'))
    except Exception as e:
        return str(e), 500

@video.route('/compose', methods = ['POST'])
#@auth.login_required
def compose():
    if not request.form or not 'candidate_url' in request.form:
        abort(400)

    try:        
        outpath = join(current_app.root_path, 'static', 'video') 
        executor.submit(create_composite, request.form['candidate_url'], outpath)
        return redirect(url_for('video.index'))
    except Exception as e:
        return str(e), 500


def create_composite(url, outpath):  
    try:  
        compositor.createCompositeInteview(url, outpath)  
    except Exception as e:
        logging.exception(e)


#@video.route('/compose', methods = ['POST'])
#@auth.login_required
#def create_task():
#    if not request.json or not 'candidate_url' in request.json:
#        abort(400)

#    url = request.json['candidate_url']
#    compositor = CompositeVideoCreator()
#    outfile = compositor.createCompositeInteview(url)   
#    return jsonify( {'output': outfile } ), 201

class FileDetails():

    def __init__(self, name, size, ctime) :
        self.name = name
        self.size = size
        self.ctime = time.gmtime(ctime)


    def timestr(self):
        return time.strftime('%Y-%m-%d %H:%M:%S', self.ctime)


