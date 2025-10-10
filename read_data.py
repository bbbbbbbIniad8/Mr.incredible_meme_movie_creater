import json
from phases import Incredible_phases

def readScript(file_path):
    result = []
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    with open("uncanny.json", 'r', encoding='utf-8') as f:
        data2 = json.load(f)
            
    for value in data["script"]:
        phase = data2[value["display"]]
        if 'mus_vol' not in phase.keys():
            phase['mus_vol'] = 1.0
  
        item = Incredible_phases(pic=phase['pic'],
                                 mus=phase['mus'],
                                 mus_start_point=phase['mus_start_point'],
                                 second=phase['second'],
                                 mus_vol=phase['mus_vol'],
                                 text = value["text"])
        result.append(item)
    return data["title"], result
