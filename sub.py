from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import re
import requests

def _create_canvas(display_width, display_height):
    img = Image.new("RGB", (display_width, display_height), "black")
    draw = ImageDraw.Draw(img)
    return img, draw

def _pic_paste(base_img, image, pasteX, pasteY):
    if pasteY != 0:
        pasteY //=2
    base_img.paste(image, (pasteX, pasteY), image)
    return base_img

def _sub_pic_paste(base_img, image, scene, display_height, pasteX, pasteY):
    if image == None:
        return 
    if scene.text =='':
        pasteY = (display_height - image.size[1]) // 2
    base_img.paste(image, (pasteX, pasteY), image)
    return base_img

def _total_paste(base_img, draw, scenes, scene_index, inc_pics, sub_pics, content_list, display_height, main_paste_coord, sub_paste_coord):
    pasteX, pasteY = main_paste_coord
    base_img = _pic_paste(base_img, inc_pics[scene_index], pasteX, pasteY)
    image = sub_pics[scene_index]
    pasteX, pasteY = sub_paste_coord 
    base_img = _sub_pic_paste(base_img, image, scenes[scene_index], display_height, pasteX, pasteY)
    for i in content_list.values():
        if i.text != '':
            draw.text(i.locate, i.text, i.color, anchor=i.type, font=i.font, stroke_width=2, stroke_fill='gray')
    return base_img

def _pic_get(scenes, display_size, inc_img_size):
    inc_pics = []
    sub_pics = []
    for i in scenes:
        image = None
        if re.search(r"^https:", i.pic) == None:
            image = Image.open(i.pic).convert("RGBA").resize(inc_img_size)
        else:
            response = requests.get(i.pic)
            image = Image.open(BytesIO(response.content)).convert("RGBA").resize(inc_img_size)            
        inc_pics.append(image)

        image = None
        if i.sub_pic != "":
            if re.search(r"^https:", i.sub_pic) == None:
                image = Image.open(i.sub_pic).convert("RGBA")
            else:
                response = requests.get(i.sub_pic)
                try:
                    image = Image.open(BytesIO(response.content)).convert("RGBA")
                except:
                    print(f"エラー: {i.sub_pic}")
                    exit()

            image_width, image_height = image.size
            inc_width = inc_img_size[0]
            display_width, display_height = display_size
            new_height = int(((display_width - inc_width) / image_width) * image_height)
            if image_width > image_height and new_height < int(display_height*(2/3)):
                new_width = (display_width - inc_width)
            else:
                new_height = int(display_height*(2/3))
                new_width = int((new_height / image_height) * image_width)
            image = image.resize((new_width, new_height))

        sub_pics.append(image)
    
    return inc_pics, sub_pics

def _adjust_header_content(scenes, display_size, inc_img_size, header_font_path, header_font_Dsize):
    header_font_list = []
    display_width, display_height = display_size
    inc_width, inc_height = inc_img_size
    for i in scenes:
        header_content = i.heading
        max_width = display_width - inc_width

        low = 1
        high = header_font_Dsize
        best_font = None

        while low <= high:
            mid = (low + high) // 2
            font = ImageFont.truetype(header_font_path, mid)
            text_width = font.getbbox(header_content)[2]
            
            if text_width <= max_width:
                best_font = font
                low = mid + 1
            else:
                high = mid - 1

        header_font_list.append(best_font or ImageFont.truetype(header_font_path, header_font_Dsize))
    return header_font_list

def _text_message(message_list, start_line=False, end_line=False, display=True):
    if display == False:
        return 
    if start_line == True:
        print("=" * 20)
    for i in message_list:
        print(i)
    if end_line == True:
        print("=" * 20)
