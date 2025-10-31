import numpy as np
from moviepy.editor import VideoClip, AudioFileClip, CompositeAudioClip
from PIL import ImageFont
from moviepy.editor import concatenate_audioclips
from text_info import Text_info
import bisect
import textwrap
from pathlib import Path
from sub import _create_canvas, _total_paste ,_pic_get, _adjust_header_content, _text_message

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
        self.padding = 10        

        self.master_path = Path(save_path) / self.title
        paths = []
        for i in ["preview", "movie"]:
            self.path = Path(save_path) / self.title / i
            self.path.mkdir(parents=True, exist_ok=True)
            paths.append(self.path)
        
        self.preview_path = paths[0]
        self.movie_path = paths[1]

    def _prepare(self, text_display, only_image):
        display_size = (self.display_width, self.display_height)
        inc_img_size = (self.inc_width, self.inc_height)
        _text_message(["WELLCOME TO Mr.incredible Meme Auto Maker"], display=text_display, start_line=True, end_line=True)
        _text_message(["START PREPARE"], display=text_display, end_line=True)

        if only_image == False:
            _text_message(["|First Step: Load Music Files."], display=text_display, start_line=True)
            self._phase_mus_processing()
            self._sound_processing()
            _text_message(["|COMPLATE."], display=text_display, end_line=True)

        _text_message(["|Second Step: Load picture Files."],display=text_display, start_line=True)
        self.sub_pics, self.inc_pics = _pic_get(self.scenes, display_size, inc_img_size)
        _text_message(["|COMPLATE."], display=text_display, end_line=True)
        self.header_font_list = _adjust_header_content(self.scenes, display_size, inc_img_size, self.header_font_path, self.header_font_Dsize)
    
    def _phase_mus_processing(self): 
        self.scene_end_times = np.cumsum([s.second for s in self.scenes])
        self.final_time = self.scene_end_times[-1]

    def _sound_processing(self):
        effect_clips = []
        for i in self.scenes:
            effect_clips.append(AudioFileClip(i.mus).subclip(i.mus_start_point, i.mus_start_point+i.second).volumex(i.mus_vol))
        effect_clips = concatenate_audioclips(effect_clips)
        self.final_audio = CompositeAudioClip([effect_clips])

    def _change_content_list(self, content_list, scene_index, header_font, header_content, pics):
        if pics[scene_index] != None:
            sub_sizeY = pics[scene_index].size[1]
            if self.scenes[scene_index].text != '' :
                content_list["header"].locate[1] = int(self.display_height * 2/3)
            else:
                content_list["header"].locate[1] = (self.display_height - sub_sizeY) // 2 + sub_sizeY
            content_list["header"].type = "ma"
            content_list["text"].locate[1] = content_list["header"].locate[1] + header_font.getbbox(header_content)[3] + self.padding

    def _create_content_list(self, scene_index, header_content, commonX, header_pasteY, text_pasteY, header_font, text_content, pics):
        content_list = {"header": Text_info(header_content, [commonX, header_pasteY], "#FBFBFB", header_font, "mm"),
                        "text": Text_info(text_content, [commonX, text_pasteY], "#FF9393", self.text_font, "ma")}
        self._change_content_list(content_list, scene_index, header_font, header_content, pics)
        return content_list
    
    def _create_scene_image(self, scene_index, header_font_list, inc_pics, sub_pics):
        base_img, draw = _create_canvas(self.display_width, self.display_height)
        header_font = header_font_list[scene_index]
        commonX, header_pasteY = (self.display_width-self.inc_width)//2, self.display_height//2
        header_content = self.scenes[scene_index].heading
        text_content = "\n".join(textwrap.wrap(self.scenes[scene_index].text, width=20))
        text_pasteY = header_font.getbbox(header_content)[3] // 2 + header_pasteY + self.padding
        
        content_list = self._create_content_list(scene_index, header_content,
                                                 commonX, header_pasteY, text_pasteY, header_font, text_content, sub_pics)
        
        main_paste_coord = self.display_width-self.inc_width, self.display_height-self.inc_height
        image = sub_pics[scene_index]
        sub_paste_coord = (self.display_width-self.inc_width-image.size[0]) // 2 ,(int((self.display_height * 2/3 - image.size[1])))
        base_img = _total_paste(base_img, draw, self.scenes, scene_index,
                                inc_pics, sub_pics, content_list, self.display_height, main_paste_coord, sub_paste_coord)

        return base_img

    def _make_frame(self, t):
        scene_index = bisect.bisect_left(self.scene_end_times, t)
        return np.array(self._create_scene_image(scene_index, self.header_font_list, self.sub_pics, self.inc_pics))

    def check_scenes(self):
        display_size = (self.display_width, self.display_height)
        inc_img_size = (self.inc_width, self.inc_height)
        self._prepare(False, True)
        header_font_list = _adjust_header_content(self.scenes, display_size, inc_img_size, self.header_font_path, self.header_font_Dsize)
        images = [self._create_scene_image(i, header_font_list, self.inc_pics, self.sub_pics) for i in range(len(self.scenes))]

        for scene_index, image in enumerate(images):
            image.save(self.preview_path / f"scene{scene_index}.png")

    def run(self):
        self._prepare(True, False)
        _text_message(["|Finall Step: Create Movie."], display=True, start_line=True, end_line=True)
        clip = VideoClip(self._make_frame, duration=self.final_time)
        clip = clip.set_audio(self.final_audio)
        clip.write_videofile(str(self.movie_path / f"{self.title}.mp4"), fps=self.fps)
        _text_message(["|END"], start_line=True, end_line=True)
