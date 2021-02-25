import os

class VideoDescriptor(object) :
    
    def __init__(self, title:str, file:str, description:str, privacy:str = 'private', category:str = None, tags=[]) :
        self.title = title
        self.file = file
        self.description = description
        self.privacy = privacy
        self.category = category
        self.tags = tags
    


class LoadDescriptor(object) :

    def __init__(self, secrets_path:str, credentials_path:str, local_server:bool = False ) :
        self.local_server = local_server
        self.secrets_path = secrets_path        
        self.credentials_path = credentials_path
        self.videos = []


    def add_video(self, options: VideoDescriptor) :
        self.videos.append(options)

    def asDictionary(self) :
        d = self.__dict__
        d['videos'] = [v.__dict__ for v in self.videos]
        return d
    
        