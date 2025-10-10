import numpy as np
from moviepy.editor import VideoClip, AudioFileClip, CompositeAudioClip
from PIL import Image, ImageDraw, ImageFont
from PIL import Image
from PIL import Image
from moviepy.editor import concatenate_audioclips
from multiprocessing import freeze_support
from read_data import readScript


class Create_movies:
    def __init__(self, sizex, sizey, frame, title, font, scenes):
        self.fps = frame
        self.width, self.height = sizex, sizey
        self.title = title
        self.font = font
        self.scenes = scenes

        self.end = False
        self.first = True
        self.final_time = 0

        self.new_height = 1000
        self.new_width = 1000
    
    def phase_mus_prosessing(self):
        scenes_second = [i.second for i in self.scenes]
        self.stack_time_lst = []
        sum = 0
        for i in scenes_second:
            sum += i
            self.stack_time_lst.append(sum)
        print(len(self.stack_time_lst),self.stack_time_lst)
        self.final_time = self.stack_time_lst[-1]

    def sound_prosessing(self):
        effect_clips = []
        for i in self.scenes:
            effect_clips.append(AudioFileClip(i.mus).subclip(i.mus_start_point, i.mus_start_point+i.second).volumex(i.mus_vol))
        effect_clips = concatenate_audioclips(effect_clips)
        self.final_audio = CompositeAudioClip([effect_clips])

    def pic_paste(self, path):
        self.image = Image.open(path).convert("RGBA")
        self.resized_image = self.image.resize((self.new_width, self.new_height))
        self.img.paste(self.resized_image, (self.width-self.new_width, 0), self.resized_image)

    def make_frame(self, t):
        self.img = Image.new("RGB", (self.width, self.height), "black")
        self.draw = ImageDraw.Draw(self.img)
        font = ImageFont.truetype(f'{self.font}', 75)

        if t >= self.stack_time_lst[self.now_cut]:
            self.now_cut += 1
            if self.stack_time_lst[self.now_cut] == self.final_time:
                self.end = True  
                return np.array(self.img)

        self.pic_paste(self.scenes[self.now_cut].pic)
        self.draw.text((210,
                        self.height//2-70), 
                        phases[self.now_cut].text,
                        "#FBFBFB",
                        font=font,
                        stroke_width=2,
                        stroke_fill='gray')

        return np.array(self.img)
    
    def final_prossessing(self):
        self.now_cut = 0
        clip = VideoClip(self.make_frame, duration=self.final_time)
        clip = clip.set_audio(self.final_audio)
        clip.write_videofile(f"./{self.title}.mp4", fps=self.fps)

    def run(self):
        self.phase_mus_prosessing()
        self.sound_prosessing()
        self.final_prossessing()


title, phases = readScript('script copy.json')

if __name__ == '__main__':
    freeze_support()    
    movie = Create_movies(
        sizex=1920,
        sizey=1080,
        frame=5,
        title=title,
        font="fonts/GenEiNuGothic-EB.ttf",
        scenes=phases
    )
    movie.run()
