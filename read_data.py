import json
from phases import Incredible_phases
import time

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
  
        item = Incredible_phases(pic=phase['pic'],
                                 mus=phase['mus'],
                                 mus_start_point=phase['mus_start_point'],
                                 second=phase['second'],
                                 mus_vol=phase['mus_vol'],
                                 heading = value['heading'],
                                 text=value['text'])
        result.append(item)
    
    if 'title' not in data.keys():
        data['title'] = time.time()
    if 'frame' not in data.keys():
        data['frame'] = 5
    if 'font_path' not in data.keys():
        print('エラー: font_pathが設定されていません。')
        exit()
    if 'save_path' not in data.keys():
        data['save_path'] = '.'

    return data['title'], data['frame'], data['font_path'], data['save_path'], result
