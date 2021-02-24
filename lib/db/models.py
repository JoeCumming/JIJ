from lib.db import db

class Video(db.Model):
    __tablename__ = 'video'

    id             = db.Column(db.Integer, primary_key=True)
    name           = db.Column(db.String())
    title          = db.Column(db.String())
    description    = db.Column(db.String())
    jij_url        = db.Column(db.String())
    composite_name = db.Column(db.String())
    composite_url  = db.Column(db.String())
    youtube_url    = db.Column(db.String())
    status         = db.Column(db.String())
    created        = db.Column(db.Boolean())
    uploaded       = db.Column(db.Boolean())
    error          = db.Column(db.Boolean())

    def __init__(self, name="", title="", description="", jij_url="", composite_name="", composite_url="", youtube_url="",
                created = False, uploaded = False):
        self.name           = name
        self.title          = title
        self.description    = description
        self.jij_url        = jij_url
        self.composite_name = composite_name
        self.composite_url  = composite_url
        self.youtube_url    = youtube_url
        self.created        = created
        self.uploaded       = uploaded
        self.error          = False
        self.status         = ""


    def __repr__(self):
        return '<id {}>'.format(self.id)
        