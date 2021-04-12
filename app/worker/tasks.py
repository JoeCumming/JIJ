
from flask_socketio import SocketIO
from app import celery, db, socketio, Config
from lib.video.creator import VideoCreator
from lib.db.models import Video
import logging

from proglog import ProgressBarLogger

class StatusUpdater(ProgressBarLogger):

    def __init__(self, video, session, message_queue):
        super().__init__()
        self.video = video
        self.session = session
        self.socketio = SocketIO(message_queue=message_queue)

    def info(self, message):
        try:
            self.video.status = message        
            self.socketio.emit('info', {'id': self.video.id, 'msg': message }, namespace = '/events')
        finally:
            self.session.commit()

    def updatename(self, name):
        self.socketio.emit('name', {'id': self.video.id, 'msg': name }, namespace = '/events')

    def update(self):
        self.socketio.emit('update', namespace = '/events')

    def complete(self):
        self.socketio.emit('complete')

    def callback(self, **changes):
        for (parameter, new_value) in changes.items():
            self.info(new_value)


@celery.task
def create_video(id: int, rootpath: str):    
    
    try:    
        video = Video.query.get(id)        
        updater = StatusUpdater(video, db.session, Config.CELERY_BROKER_URL)

        try:                      
            VideoCreator(video, rootpath, updater).createAndUpload()        
        except Exception as e:
            logging.exception(e)
            video.error = True
            video.status = 'Error : ' + str(e)        
            db.session.commit()
            updater.complete()
    finally:
        db.session.commit()
        updater.update()
        
    