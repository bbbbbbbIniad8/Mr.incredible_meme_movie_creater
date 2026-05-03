import numpy as np
from moviepy.editor import VideoClip, AudioFileClip, CompositeAudioClip
from PIL import ImageFont
from moviepy.editor import concatenate_audioclips
from text_info import Text_info
import bisect
import textwrap
from pathlib import Path
from sub import _create_canvas, _total_paste, _pic_get, _adjust_header_content, _text_message, _decide_best_font, _create_content_list, _decide_sub_paste_coord

class Create_movies:
    def __init__(self, title, frame,  font, font_size, font2, font2_size, save_path, scenes, mode = "nomral"):
        self.fps = frame
        if mode == "normal":
            self.display_width, self.display_height = 1920, 1080
            self.inc_width, self.inc_height = 900, 900
        else:
            self.display_width, self.display_height = 1080, 1920
            self.inc_width, self.inc_height = 300, 300
        self.mode = mode
        self.title = title
        self.header_font_path = font
        self.header_font_Dsize = font_size
        self.text_font = ImageFont.truetype(font2, font2_size)
        self.save_path = save_path
        self.scenes = scenes
        if self.mode == "short":
            self._short_processing()
        self.padding = 10        

        self.master_path = Path(save_path) / self.title
        paths = []
        for i in ["preview", "movie"]:
            self.path = Path(save_path) / (self.title + "-" + self.mode) / i
            self.path.mkdir(parents=True, exist_ok=True)
            paths.append(self.path)
        
        self.preview_path = paths[0]
        self.movie_path = paths[1]
        self.base_line_coord = int((self.display_height * 0.5))
        self.inc_paste_coord = [self.display_width-self.inc_width,
                                (self.display_height-self.inc_height)//2 if self.mode == "normal" else self.base_line_coord - (self.inc_height)]

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
        self.sub_pics, self.inc_pics = _pic_get(self.scenes, display_size, inc_img_size, self.mode)
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

    def _short_processing(self):
        max_width = self.display_width
        font_path = self.header_font_path
        font_max_size = 200
        font = _decide_best_font(self.scenes[0].heading, max_width, font_path, font_max_size)
        self.poptitle_info = Text_info(self.scenes[0].heading, (max_width//2, 150), "white", font, "ma")
        self.scenes = self.scenes[1:]
    
    def _create_scene_image(self, scene, header_font_list, pics):
        base_img, draw = _create_canvas(self.display_width, self.display_height)
        header_font = header_font_list
        header_content = scene.heading
        text_content = "\n".join(textwrap.wrap(scene.text, width=20))
        commonX = (self.display_width-self.inc_width)//2 if self.mode == "normal" else self.display_width//2
        sub_paste_coord = _decide_sub_paste_coord(pics, self.display_width, self.display_height, 
                                                  self.base_line_coord, self.inc_width, scene.text, self.mode)
        content_list = _create_content_list(scene, header_content,
                                            commonX, 0, 0, header_font, self.text_font, text_content, pics["sub"],
                                            self.display_height, self.base_line_coord, self.padding, self.mode)
        poptitle_info = self.poptitle_info if self.mode == "short" else None
        base_img = _total_paste(base_img, draw,
                                pics, content_list, self.inc_paste_coord, sub_paste_coord,
                                poptitle_info)

        return base_img

    def _make_frame(self, t):
        scene_index = bisect.bisect_left(self.scene_end_times, t)
        return np.array(self._create_scene_image(self.scenes[scene_index],
                                                 self.header_font_list[scene_index],
                                                 {"inc": self.sub_pics[scene_index], 
                                                  "sub": self.inc_pics[scene_index]}))

    def check_scenes(self):
        display_size = (self.display_width, self.display_height)
        inc_img_size = (self.inc_width, self.inc_height)
        self._prepare(False, True)
        header_font_list = _adjust_header_content(self.scenes, display_size, inc_img_size, self.header_font_path, self.header_font_Dsize)
        images = [self._create_scene_image(v,
                                           header_font_list[i], 
                                           {"inc": self.sub_pics[i], 
                                            "sub": self.inc_pics[i]}) for i, v in enumerate(self.scenes)]

        for scene_index, image in enumerate(images):
            image.save(self.preview_path / f"scene{scene_index}.png")

    def run(self):
        self._prepare(True, False)
        _text_message(["|Finall Step: Create Movie."], display=True, start_line=True, end_line=True)
        clip = VideoClip(self._make_frame, duration=self.final_time)
        clip = clip.set_audio(self.final_audio)
        clip.write_videofile(str(self.movie_path / f"{self.title}.mp4"), fps=self.fps)
        _text_message(["|END"], start_line=True, end_line=True)
