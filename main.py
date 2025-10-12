from io import BytesIO
import numpy as np
from moviepy.editor import VideoClip, AudioFileClip, CompositeAudioClip
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import concatenate_audioclips
from multiprocessing import freeze_support
from read_data import readScript
from text_info import Text_info
import bisect
import textwrap
import re
import requests

class Create_movies:
    def __init__(self, sizex, sizey, title, frame,  font, font_size, font2, font2_size, save_path, scenes):
        self.fps = frame
        self.display_width, self.display_height = sizex, sizey
        self.title = title
        self.header_font_path = font
        self.header_font_Dsize = font_size
        self.text_font = ImageFont.truetype(font2, font2_size)
        self.save_path = save_path
        self.scenes = scenes
        self.inc_width, self.inc_height = 900, 900
        # self.sub_width, self.sub_height = 900, 900
        self.padding = 10

        self._phase_mus_processing()
        self._pic_get()
        self._sound_processing()
        self._adjust_header_content()
    
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
        self.inc_pics = []
        self.sub_pics = []
        for i in self.scenes:
            image = None
            if re.search(r"^https:", i.pic) == None:
                image = Image.open(i.pic).convert("RGBA").resize((self.inc_width, self.inc_height))
            else:
                response = requests.get(i.pic)
                image = Image.open(BytesIO(response.content)).convert("RGBA").resize((self.inc_width, self.inc_height))            
            self.inc_pics.append(image)

            image = None
            if i.sub_pic != "":
                if re.search(r"^https:", i.sub_pic) == None:
                    image = Image.open(i.sub_pic).convert("RGBA")
                else:
                    response = requests.get(i.sub_pic)
                    image = Image.open(BytesIO(response.content)).convert("RGBA")

                image_width, image_height = image.size
                new_height = int(self.display_height*(2/3))
                new_width = int((new_height / image_height) * image_width)
                image.resize((new_width, new_height))
            self.sub_pics.append(image)

    def _pic_paste(self, image):
        pasteX, pasteY = self.display_width-self.inc_width, self.display_height-self.inc_height
        if pasteY != 0:
            pasteY //=2
        self.img.paste(image, (pasteX, pasteY), image)

    def _sub_pic_paste(self, image, scene_index):
        if image == None:
            return 
        pasteX, pasteY = (self.display_width-self.inc_width-image.size[0]) // 2, 0
        if self.scenes[scene_index].text =='':
            pasteY = (self.display_height - image.size[1]) // 2
        self.img.paste(image, (pasteX, pasteY), image)

    def _adjust_header_content(self):
        self.header_font_list = []
        for i in self.scenes:
            header_content = i.heading
            max_width = self.display_width - self.inc_width

            low = 1
            high = self.header_font_Dsize
            best_font = None

            while low <= high:
                mid = (low + high) // 2
                font = ImageFont.truetype(self.header_font_path, mid)
                text_width = font.getbbox(header_content)[2]
                
                if text_width <= max_width:
                    best_font = font
                    low = mid + 1
                else:
                    high = mid - 1

            self.header_font_list.append(best_font or ImageFont.truetype(self.header_font_path, self.header_font_Dsize))

    def change_content_list(self, content_list, scene_index, header_font, header_content):
        sub_sizeY = self.sub_pics[scene_index].size[1]
        if self.sub_pics[scene_index] != None:
            if self.scenes[scene_index].text != '' :
                content_list["header"].locate[1] = sub_sizeY
            else:
                content_list["header"].locate[1] = (self.display_height - sub_sizeY) // 2 + sub_sizeY
            content_list["header"].type = "ma"
            content_list["text"].locate[1] = content_list["header"].locate[1] + header_font.getbbox(header_content)[3] + self.padding


    def _make_frame(self, t):
        self.img = Image.new("RGB", (self.display_width, self.display_height), "black")
        self.draw = ImageDraw.Draw(self.img)
        scene_index = bisect.bisect_left(self.scene_end_times, t)
        header_font = self.header_font_list[scene_index]
        commonX, header_pasteY = (self.display_width-self.inc_width)//2, self.display_height//2
        header_content = self.scenes[scene_index].heading
        text_content = "\n".join(textwrap.wrap(self.scenes[scene_index].text, width=17))
        text_pasteY = header_font.getbbox(header_content)[3] // 2 + header_pasteY + self.padding
        
        content_list = {"header": Text_info(header_content, [commonX, header_pasteY], "#FBFBFB", header_font, "mm"),
                        "text": Text_info(text_content, [commonX, text_pasteY], "#FF9393", self.text_font, "ma")}

        self.change_content_list(content_list, scene_index, header_font, header_content)

        if scene_index >= len(self.scenes):
            scene_index = len(self.scenes) - 1

        self._pic_paste(self.inc_pics[scene_index])
        self._sub_pic_paste(self.sub_pics[scene_index], scene_index)

        for i in content_list.values():
            if i.text != '':
                self.draw.text(i.locate, i.text, i.color, anchor=i.type, font=i.font, stroke_width=2, stroke_fill='gray')

        return np.array(self.img)
    
    def run(self):
        clip = VideoClip(self._make_frame, duration=self.final_time)
        clip = clip.set_audio(self.final_audio)
        clip.write_videofile(self.save_path+f"/{self.title}.mp4", fps=self.fps)


info = readScript('./private_file/test.json', 'uncanny.json')

if __name__ == '__main__':
    freeze_support()    
    movie = Create_movies(1920, 1080, info.title, info.frame, info.header_font_path, info.header_size,
                          info.text_font_path, info.text_size, info.save_path, info.scenes)
    movie.run()
