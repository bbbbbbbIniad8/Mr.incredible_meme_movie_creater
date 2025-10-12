import json
from phases import Incredible_phases
import time

class Read_result_info:
    def __init__(self, title, frame, font_path, font_size, font2_path, font2_size, save_path, scenes):
        self.title = title
        self.frame = frame
        self.header_font_path = font_path
        self.header_size = font_size
        self.text_font_path = font2_path
        self.text_size = font2_size
        self.save_path = save_path
        self.scenes = scenes
        self.new_height, self.new_width = 900, 900
        self.padding = 10


def readScript(file_path, phase_path):
    result = []
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    with open(phase_path, 'r', encoding='utf-8') as f:
        data2 = json.load(f)
            
    for value in data["script"]:
        phase = data2[value["display"]]
        if 'mus_vol' not in phase.keys():
            phase['mus_vol'] = 1.0
        if 'heading' not in value.keys():
            value['heading'] = ''
        if 'text' not in value.keys():
            value['text'] = ''
        if 'pic' not in value.keys():
            value['pic'] = ''
  
        item = Incredible_phases(pic=phase['pic'],
                                 mus=phase['mus'],
                                 mus_start_point=phase['mus_start_point'],
                                 second=phase['second'],
                                 mus_vol=phase['mus_vol'],
                                 heading = value['heading'],
                                 text=value['text'],
                                 sub_pic_path=value['pic'])
        result.append(item)
    
    if 'title' not in data.keys():
        data['title'] = time.time()
    if 'frame' not in data.keys():
        data['frame'] = 5
    if 'header_font_path' not in data.keys() or 'text_font_path' not in data.keys():
        print('エラー: font_pathが設定されていません。')
        exit()
    if 'header_font_size' not in data.keys():
        data['header_font_size'] = 55
    if 'text_font_size' not in data.keys():
        data['text_font_size'] = 45
    if 'save_path' not in data.keys():
        data['save_path'] = '.'
    
    

    result2 = Read_result_info(data['title'], data['frame'], data['header_font_path'], data['header_font_size'],
                               data['text_font_path'], data['text_font_size'], data['save_path'], result)

    return result2
