
from flask_socketio import SocketIO
from app import celery, db, socketio, Config
from lib.video.creator import VideoCreator
from lib.db.models import Video
import logging

from proglog import ProgressBarLogger

class StatusUpdater(ProgressBarLogger):

    def __init__(self, id, message_queue):
        super().__init__()
        self.id = id
        self.socketio = SocketIO(message_queue=message_queue)

    def info(self, id, message):
        self.socketio.emit('info', {'id': id, 'msg': message }, namespace = '/events')

    def update(self):
        self.socketio.emit('update', namespace = '/events')

    def complete(self):
        self.socketio.emit('complete')

    def callback(self, **changes):
        for (parameter, new_value) in changes.items():
            self.info(self.id, new_value)


@celery.task
def create_video(videoid: int, rootpath: str):    
    
    try:    
        video = Video.query.get(videoid)        
        updater = StatusUpdater(video.id, Config.CELERY_BROKER_URL)

        try:                      
            VideoCreator(video, rootpath, db.session, updater).createAndUpload()        
        except Exception as e:
            logging.exception(e)
            video.error = True
            video.status = 'Error : ' + str(e)        
            db.session.commit()
            updater.complete()
    finally:
        db.session.commit()
        updater.update()
        
    