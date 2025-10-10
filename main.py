import numpy as np
from moviepy.editor import VideoClip, AudioFileClip, CompositeAudioClip
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import concatenate_audioclips
from multiprocessing import freeze_support
from read_data import readScript
import bisect


class Create_movies:
    def __init__(self, sizex, sizey, frame, title, font, scenes):
        self.fps = frame
        self.width, self.height = sizex, sizey
        self.title = title
        self.font = ImageFont.truetype(font, 75)
        self.scenes = scenes
        self.new_height, self.new_width = 1000, 1000

        self._phase_mus_processing()
        self._pic_get()
        self._sound_processing()
    
    def _phase_mus_processing(self):
        self.scene_end_times = np.cumsum([s.second for s in self.scenes])
        self.final_time = self.scene_end_times[-1]

    def _sound_processing(self):
        effect_clips = []
        for i in self.scenes:
            effect_clips.append(AudioFileClip(i.mus).subclip(i.mus_start_point, i.mus_start_point+i.second).volumex(i.mus_vol))
        effect_clips = concatenate_audioclips(effect_clips)
        self.final_audio = CompositeAudioClip([effect_clips])

    def _pic_get(self):
        self.pics = []
        for i in self.scenes:
            self.image = Image.open(i.pic).convert("RGBA").resize((self.new_width, self.new_height))
            self.pics.append(self.image)

    def _pic_paste(self, image):
        self.img.paste(image, (self.width-self.new_width, 0), image)

    def _make_frame(self, t):
        self.img = Image.new("RGB", (self.width, self.height), "black")
        self.draw = ImageDraw.Draw(self.img)
        scene_index = bisect.bisect_left(self.scene_end_times, t)
        
        if scene_index >= len(self.scenes):
            scene_index = len(self.scenes) - 1

        self._pic_paste(self.pics[scene_index])
        self.draw.text((210,
                        self.height//2-70), 
                        self.scenes[scene_index].text,
                        "#FBFBFB",
                        font=self.font,
                        stroke_width=2,
                        stroke_fill='gray')

        return np.array(self.img)
    
    def run(self):
        clip = VideoClip(self._make_frame, duration=self.final_time)
        clip = clip.set_audio(self.final_audio)
        clip.write_videofile(f"./private_file/{self.title}.mp4", fps=self.fps)


title, scenes = readScript('private_file/script copy.json')

if __name__ == '__main__':
    freeze_support()    
    movie = Create_movies(
        sizex=1920,
        sizey=1080,
        frame=5,
        title=title,
        font="fonts/GenEiNuGothic-EB.ttf",
        scenes=scenes
    )
    movie.run()
