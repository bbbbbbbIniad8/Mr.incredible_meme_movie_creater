import numpy as np
from moviepy.editor import VideoClip, AudioFileClip, CompositeAudioClip
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import concatenate_audioclips
from multiprocessing import freeze_support
from read_data import readScript
from text_info import Text_info
import bisect
import textwrap


class Create_movies:
    def __init__(self, sizex, sizey, frame, title, font, save_path, scenes):
        self.fps = frame
        self.width, self.height = sizex, sizey
        self.title = title
        self.header_font = ImageFont.truetype(font, 55)
        self.text_font = ImageFont.truetype("fonts/Honoka_Shin_Mincho_L.otf", 45)
        self.save_path = save_path
        self.scenes = scenes
        self.new_height, self.new_width = 900, 900
        self.padding = 10

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
        pasteX, pasteY = self.width-self.new_width, self.height-self.new_height
        if pasteY != 0:
            pasteY //=2
        self.img.paste(image, (pasteX, pasteY), image)

    def _make_frame(self, t):
        self.img = Image.new("RGB", (self.width, self.height), "black")
        self.draw = ImageDraw.Draw(self.img)
        scene_index = bisect.bisect_left(self.scene_end_times, t)
        commonX, commonY = (self.width-self.new_width)//2, self.height//2
        header_content = self.scenes[scene_index].heading
        text_content = "\n".join(textwrap.wrap(self.scenes[scene_index].text, width=17))
        textY = self.header_font.getbbox(header_content)[3] // 2 + commonY + self.padding
        content_list = [Text_info(header_content, (commonX, commonY), "#FBFBFB", self.header_font, "mm"),
                        Text_info(text_content, (commonX, textY), "#FF9393", self.text_font, "ma")]

        if scene_index >= len(self.scenes):
            scene_index = len(self.scenes) - 1

        self._pic_paste(self.pics[scene_index])

        for i in content_list:
            if i.text != '':
                self.draw.text(i.locate, i.text, i.color, anchor=i.type, font=i.font, stroke_width=2, stroke_fill='gray')

        return np.array(self.img)
    
    def run(self):
        clip = VideoClip(self._make_frame, duration=self.final_time)
        clip = clip.set_audio(self.final_audio)
        clip.write_videofile(self.save_path+f"/{self.title}.mp4", fps=self.fps)


title, frame, font_path, save_path, scenes = readScript('./private_file/black.json',
                                                        'uncanny.json')

if __name__ == '__main__':
    freeze_support()    
    movie = Create_movies(1920, 1080, frame, title, font_path, save_path, scenes)
    movie.run()
