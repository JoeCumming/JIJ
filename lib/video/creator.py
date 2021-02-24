
import logging
import os
import requests
import re
import tempfile
from bs4 import BeautifulSoup
from youtube_video_upload import upload_from_options

from lib.db.models import Video
from lib.video.compositor import Answer, CompositeVideoCreator
from lib.video.options import VideoDescriptor, LoadDescriptor


class VideoCreator(object):

    PRIVACY = 'unlisted'
    CATEGORY = 'Education'

    def __init__(self, appcontext, id: int, video:Video):
        self.compositor = CompositeVideoCreator()        
        self.appcontext = appcontext
        self.id = str(id)
        self.video = video        
        self.dbsession= appcontext.db.session
        self.config= appcontext.config

    def status(self, message: str):
        self.appcontext.status(message)    

    def info(self, message: str, tag:str =""):
        self.appcontext.info(tag + self.id, message)    

    def createAndUpload(self):        

        self.info('Creating composite video...')
        self.create()
        self.info('Composite video created')

        secrets_file = self.config.get('SECRETS_FILE')
        credentials_file = self.config.get('CREDENTIALS_FILE')
        loader = LoadDescriptor(secrets_file, credentials_file, True)  
        loader.add_video(VideoDescriptor(self.video.title, self.video.composite_url, self.video.title, VideoCreator.PRIVACY, VideoCreator.CATEGORY))

        self.video.status = "Loading to YouTube ..."      
        self.dbsession.commit()
        self.info(self.video.status)        
            
        youtube_url = upload_from_options(loader.asDictionary())
        self.video.youtube_url = youtube_url
        self.video.uploaded = True
        self.video.status = ""      
        self.dbsession.commit()
        
        return youtube_url


    def create(self):
        
        self.appcontext.push()

        self.dbsession.add(self.video)
        source_url = self.video.jij_url
        
        self.info('Parsing ' + source_url)

        page = requests.get(source_url)
        soup = BeautifulSoup(page.content, 'html.parser')

        name = self.getApplicantName(soup)
        self.video.name = name
        self.dbsession.commit()
        self.info(name, "name")

        answervideos = self.getApplicantVideos(soup, name)                
        videofilename = name.replace(" ", "") + ".mp4"
        videofilepath = os.path.join(self.appcontext.root_path(), 'static', 'video', videofilename) 
        
        self.video.name = name
        self.video.title = name + " Video Interview"
        self.video.description = "JobsInJapan.com First Round Inteview"          
        self.video.composite_name = videofilename
        self.video.composite_url = videofilepath
        self.video.status = "Writing concatenated video ..."        
        self.dbsession.commit()

        self.info(self.video.status)        
        
        self.compositor.createCompositeInteview(name, source_url, videofilepath, answervideos)          
        self.video.created = True
        self.video.status = "Concatenated video complete"        
        self.dbsession.commit()
        self.info(self.video.status)                

    
    def getApplicantName(self, soup):
        information = soup.find('div', {'id': 'vidcruiter-public-profile-applicant'})
        return information.find('p', class_='name').text.strip()


    def getApplicantVideos(self, soup, name: str):
        applicant = name.replace(" ", "_")
        tempdir = tempfile.gettempdir()
        videos = []

        qandasection = soup.find_all('div', class_='vidcruiter-public-profile-question-page-answer')
        i = 0
        for div in qandasection:
            question_div = div.find('div', class_='question')
            question = str.strip(question_div.find('div', class_='description').text)
            answer_div = div.find('div', class_='answer')
            answer_video = answer_div.find('source').attrs['src']      

            video = os.path.join(tempdir, '{}_{}.mp4'.format(applicant, i))
                    
            if not os.path.exists(video):
                with requests.get(answer_video, allow_redirects=True) as r:
                    logging.info("Saving answer {} to {}".format(i, video))
                    self.info("Saving answer {}".format(i))
                    with open(video, 'wb') as local:
                        local.write(r.content)

            videos.append(Answer(question, video))    
            i = i + 1

        return videos
