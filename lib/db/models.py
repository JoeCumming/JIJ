from lib.db import db

class Video(db.Model):
    __tablename__ = 'video'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    description = db.Column(db.String())
    jij_url = db.Column(db.String())
    composite_url = db.Column(db.String())
    youtube_url = db.Column(db.String())

    def __init__(self, name="", description="", jij_url="", composite_url="", youtube_url=""):
        self.name = name
        self.description = description
        self.jij_url = jij_url
        self.composite_url = composite_url
        self.youtube_url = youtube_url

    def __repr__(self):
        return '<id {}>'.format(self.id)
        