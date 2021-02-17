import requests
import logging
import tempfile
import os 
from bs4 import BeautifulSoup
from moviepy.editor import *

from videoprops import get_video_properties, get_audio_properties

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

class Size:
    def __init__(self, height, width):
        self.height = height
        self.width = width
    

class Answer:
    def __init__(self, question, video):
        self.question = question
        self.video = video
        self.videoprops = get_video_properties(video)
        self.audioprops = get_audio_properties(video)

    def createVideoClip(self, videosize: Size, fontsize:int, logo):
        title = (TextClip(self.question, fontsize=fontsize, font="Noto-Sans-Regular", color='white', size=(videosize.height*0.9, videosize.width*0.25), method="caption")
                    .set_position(('center',0.6), relative=True)
                    .set_duration(4)
                    .fadein(1).fadeout(1))
        answer = VideoFileClip(self.video).fadein(1).fadeout(1)        
        return CompositeVideoClip([answer, title, logo])

    def getSize(self):
        return Size(self.videoprops['height'], self.videoprops['width'])

    def getBitrate(self):
        return self.videoprops['bit_rate']
            
    def getAudioBitrate(self):
        return self.audioprops['bit_rate']


class CompositeVideoCreator:
    
    REFERENCE_HEIGHT = 360
    BASE_ANSWER_FONTSIZE = 18
    BASE_TITLE_FONTSIZE = 30
    BASE_BITRATE = '347072'
    BASE_AUDIO_BITRATE = '71224'

    def __init__(self, title_logo='./img/title_logo.png', answer_logo='./img/answer_logo.png') :
        self.title_logo = title_logo
        self.answer_logo = answer_logo

    def createCompositeInteview(self, url:str, outpath:str=None, framerate=25, bitrate=None, audio_bitrate=None):

        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')

        name = self.getApplicantName(soup)
        outfile = os.path.join(outpath if outpath != None else tempfile.gettempdir(), "{}_complete.mp4".format(name.replace(" ", "_")))

        if not os.path.exists(outfile) :
            answervideos = self.getApplicantVideos(soup, name)
            
            videoprops = self.getVideoProperties(answervideos[0].video)
            targetsize = answervideos[0].getSize()        
            bitrate = bitrate if not bitrate is None else answervideos[0].getBitrate()
            audio_bitrate = audio_bitrate if not audio_bitrate is None else answervideos[0].getAudioBitrate()
            answerlogoclip = self.getAnswerLogoClip()
            fontscale = targetsize.height / CompositeVideoCreator.REFERENCE_HEIGHT
            answerfontsize = int(CompositeVideoCreator.BASE_ANSWER_FONTSIZE * fontscale)
            titlefontsize = int(CompositeVideoCreator.BASE_TITLE_FONTSIZE * fontscale)        

            answer_clips = [answer.createVideoClip(targetsize, answerfontsize, answerlogoclip) for answer in answervideos]
            opening_clip = [self.createTitleClip(name, targetsize, titlefontsize, self.getTitleLogoClip(80 * fontscale))]
            closing_clip = [self.createClosingClip(targetsize, titlefontsize, self.getClosingLogoClip(50 * fontscale))]
            clips = opening_clip + answer_clips + closing_clip
            
            final_clip = concatenate_videoclips(clips)
            logging.info("Writing concatenated video to {}".format(outfile))
            final_clip.write_videofile(outfile, fps=framerate, bitrate=bitrate, audio_bitrate=audio_bitrate)

        return outfile
        
    def getAnswerLogoClip(self, height: int = 30):
        return (ImageClip(self.answer_logo, duration=10)          
                .resize(height=height)
                .margin(right=8, top=8, opacity=0)
                .set_position(("right","top"))
                .fadein(0.5))

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
                    with open(video, 'wb') as local:
                        local.write(r.content)

            videos.append(Answer(question, video))    
            i = i + 1

        return videos

    def getVideoProperties(self, video: str):
        return get_video_properties(video)   

    def getAudioProperties(self, video: str):
        return get_audio_properties(video)          

    def getVideoSize(self, props):        
        return Size(props['height'], props['width'])

    def createTitleClip(self, name: str,  size: Size, fontsize: int,logo: ImageClip):
        background = ColorClip((size.width, size.height))
        titleclip = TextClip(name, fontsize=fontsize, font="Noto-Sans-Regular", color='white').set_position('center')
        subtitleclip = (TextClip("First round interview", fontsize=15, font="Noto-Sans-Regular", color='white')
                        .set_position(('center',0.55), relative=True))
                    
        return CompositeVideoClip([background, titleclip, subtitleclip, logo]).set_duration(3).fadein(1).fadeout(1) 


    def getTitleLogoClip(self, height:int) :
        return (ImageClip(self.title_logo, duration=10)          
            .resize(height=height)
            .margin(top=16, opacity=0)
            .set_position(('center',0.18), relative=True))
        

    def createClosingClip(self, size:Size, fontsize:int, logo:ImageClip):
        background = ColorClip((size.width, size.height))
        clip = TextClip("www.jobsinjapan.com", fontsize=fontsize, font="Noto-Sans-Regular", color='white').set_position('center')            
        video = CompositeVideoClip([background, clip, logo]).set_duration(5).fadein(1).fadeout(1)           
        return video

    def getClosingLogoClip(self, height:int) :
        return(ImageClip(self.title_logo, duration=10)          
            .resize(height=height)
            .margin(top=16, opacity=0)
            .set_position(('center',0.24), relative=True))
