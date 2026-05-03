from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import re
import requests
from text_info import Text_info

def _create_canvas(display_width, display_height):
    img = Image.new("RGB", (display_width, display_height), "black")
    draw = ImageDraw.Draw(img)
    return img, draw

def _pic_paste(base_img, image, paste_coord):
    base_img.paste(image, paste_coord, image)
    return base_img

def _sub_pic_paste(base_img, image, paste_coord):
    if image != None:
        base_img.paste(image, paste_coord, image)
    return base_img

def _total_paste(base_img, draw, pics, content_list, main_paste_coord, sub_paste_coord, poptitle_info):
    if poptitle_info != None:
        item = poptitle_info
        draw.text(item.locate, item.text, item.color, anchor=item.type, font=item.font, stroke_width=2, stroke_fill='gray')

    base_img = _pic_paste(base_img, pics["inc"], main_paste_coord) 
    base_img = _sub_pic_paste(base_img, pics["sub"], sub_paste_coord)
    for i in content_list.values():
        if i.text != '':
            draw.text(i.locate, i.text, i.color, anchor=i.type, font=i.font, stroke_width=2, stroke_fill='gray')
    return base_img

def _pic_get(scenes, display_size, inc_img_size, mode):
    inc_pics, sub_pics = [], []
    for i in scenes:
        inc_image = get_inc_pic(i.pic, inc_img_size)       
        inc_pics.append(inc_image)
        image = get_sub_pic(i.sub_pic)
        if image != None:
            image = _resize_pic(image, inc_img_size, display_size, mode)
        sub_pics.append(image)
    return inc_pics, sub_pics

def get_inc_pic(path, inc_img_size):
    if re.search(r"^https:", path) == None:
        image = Image.open(path).convert("RGBA").resize(inc_img_size)
    else:
        response = requests.get(path)
        image = Image.open(BytesIO(response.content)).convert("RGBA").resize(inc_img_size)            
    return image

def get_sub_pic(path):
    if path == "":
        return None
    if re.search(r"^https:", path) == None:
        image = Image.open(path).convert("RGBA")
    else:
        image = _pic_download(path)
    return image

def _pic_download(path):
    response = requests.get(path)
    try:
        image = Image.open(BytesIO(response.content)).convert("RGBA")
    except:
        print(f"エラー: {path}")
        exit()
    return image

def _resize_pic(image, inc_img_size, display_size, mode):
    image_width, image_height = image.size
    inc_width = inc_img_size[0]
    display_width, display_height = display_size
    new_height = int(((display_width - inc_width) / image_width) * image_height)
    if mode == "normal":
        height_max = 2/3
    else:
        height_max = 1/3

    if image_width > image_height and new_height < int(display_height*(height_max)):
        new_width = (display_width - inc_width)
    else:
        new_height = int(display_height*(height_max))
        new_width = int((new_height / image_height) * image_width)
    image = image.resize((new_width, new_height))
    return image

def _adjust_header_content(scenes, display_size, inc_img_size, header_font_path, header_font_Dsize):
    header_font_list = []
    display_width = display_size[0]
    inc_width = inc_img_size[0]
    for i in scenes:
        header_content = i.heading
        max_width = display_width - inc_width
        best_font = _decide_best_font(header_content, max_width, header_font_path, header_font_Dsize)
        header_font_list.append(best_font or ImageFont.truetype(header_font_path, header_font_Dsize))
    return header_font_list

def _decide_best_font(content, max_width, font_path, font_max_size):
    low = 1
    high = font_max_size
    best_font = None
    while low <= high:
        mid = (low + high) // 2
        font = ImageFont.truetype(font_path, mid)
        text_width = font.getbbox(content)[2]
        
        if text_width <= max_width:
            best_font = font
            low = mid + 1
        else:
            high = mid - 1
    return best_font

def _text_message(message_list, start_line=False, end_line=False, display=True):
    line = "=" * 20
    if display == False:
        return 
    if start_line == True:
        print(line)
    for i in message_list:
        print(i)
    if end_line == True:
        print(line)

def _create_content_list(scene_index, header_content, commonX, header_pasteY, text_pasteY, header_font, text_font, text_content, pics, display_height, base_line_coord, padding, mode):
        content_list = {"header": Text_info(header_content, [commonX, header_pasteY], "#FBFBFB", header_font, "mm"),
                        "text": Text_info(text_content, [commonX, text_pasteY], "#FF9393", text_font, "ma")}
        content_list = _change_content_list(content_list, scene_index, header_font, header_content, pics, mode, display_height, base_line_coord, padding)
        return content_list

def _change_content_list(content_list, scene, header_font, header_content, sub_pic, mode, display_height, base_line_coord, padding):
        if mode == "normal":
            if sub_pic != None:
                sub_sizeY = sub_pic.size[1]
                if scene.text != '' :
                    headerY = int(display_height * 2/3)
                else:
                    headerY = (display_height - sub_sizeY) // 2 + sub_sizeY
                content_list["header"].type = "ma"
            else:
                headerY = display_height // 2
        else:
            headerY =  base_line_coord + padding*10

        content_list["header"].locate[1] = headerY
        content_list["text"].locate[1] = headerY + header_font.getbbox(header_content)[3]
        return content_list

def _decide_sub_paste_coord(pics, display_width, display_height,base_line_coord, inc_width, text, mode):
    sub_paste_coord = [0, 0]
    if pics["sub"] != None:
        sub_picX, sub_picY = pics["sub"].size
        X = (display_width-inc_width-sub_picX) 
        if mode == "normal":
            Y = int((display_height * 2/3 - sub_picY) // 2)
        else:
            Y = int((base_line_coord - sub_picY))
        if text =='' and mode == "normal":
            Y = (display_height - sub_picY) // 2
        sub_paste_coord = [X//2, Y]
    return sub_paste_coord
