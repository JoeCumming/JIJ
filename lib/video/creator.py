
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

    def __init__(self, video:Video, rootpath: str, session, updater):
        self.compositor = CompositeVideoCreator()                        
        self.session = session
        self.video = video
        self.id = self.video.id     
        self.rootpath = rootpath  
        self.updater = updater      
                

    def info(self, message: str, tag:str =""):        
        self.updater.info(self.id, message)                    

    def update(self):        
        self.updater.update()                    

    def createAndUpload(self):        

        self.update()

        self.info('Creating composite video...')
        self.create()
        self.info('Composite video created')

        #secrets_file = self.config.get('SECRETS_FILE')
        #credentials_file = self.config.get('CREDENTIALS_FILE')
        #loader = LoadDescriptor(secrets_file, credentials_file, True)  
        #loader.add_video(VideoDescriptor(self.video.title, self.video.composite_url, self.video.title, VideoCreator.PRIVACY, VideoCreator.CATEGORY))
                
        self.video.status = "Loading to YouTube ..."
        self.session.commit() 

        youtube_url = "" #upload_from_options(loader.asDictionary())
        self.video.youtube_url = youtube_url
        self.video.uploaded = True
        self.video.status = ""
        self.session.commit()                
        
        self.updater.complete()          

        return youtube_url


    def create(self):
        
        source_url = self.video.jij_url        
        self.info('Parsing ' + source_url)

        page = requests.get(source_url)
        soup = BeautifulSoup(page.content, 'html.parser')

        name = self.getApplicantName(soup)
        self.video.name = name        
        self.session.commit()        
        #self.info(name, "name")
        self.update()

        answervideos = self.getApplicantVideos(soup, name)                
        videofilename = name.replace(" ", "") + ".mp4"
        videofilepath = os.path.join(self.rootpath, 'static', 'video', videofilename) 
                

        self.video.title = name + " Video Interview"
        self.video.description = "JobsInJapan.com First Round Inteview"          
        self.video.composite_name = videofilename
        self.video.composite_url = videofilepath        
        self.video.status = "Writing concatenated video ..."
        self.session.commit()        

        self.info(self.video.status)        
        
        self.compositor.createCompositeInteview(name, source_url, videofilepath, answervideos)          
        self.video.created = True
        self.video.status = "Concatenated video complete"        
        self.session.commit()        
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
