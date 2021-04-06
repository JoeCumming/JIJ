
from flask_socketio import SocketIO
from app import celery, db, socketio, Config
from lib.video.creator import VideoCreator
from lib.db.models import Video
import logging


##Not sure I should be doing this ... ?
##Session is for the app?
#class DBSessionTask(celery.Task):
#    abstract = True
#    def after_return(self, status, retval, task_id, args, kwargs, einfo):
#        db.session.remove()

class StatusUpdater():

    def __init__(self, message_queue):
        self.socketio = SocketIO(message_queue=message_queue)

    def info(self, id, message):
        self.socketio.emit('info', {'id': id, 'msg': message }, namespace = '/events')

    def update(self):
        self.socketio.emit('update', namespace = '/events')

    def complete(self):
        self.socketio.emit('complete')


@celery.task
def create_video(videoid: int, rootpath: str):    

    updater = StatusUpdater(Config.CELERY_BROKER_URL)
    try:              
        video = Video.query.get(videoid)        
        creator = VideoCreator(video, rootpath, db.session, updater)                    
        creator.createAndUpload()                
        
    except Exception as e:
        logging.exception(e)
        #creator.video.error = True
        #creator.video.status = 'Error : ' + str(e)
        #creator.appcontext.db.session.commit()  
        updater.complete()
    finally:
        updater.update()
        
    