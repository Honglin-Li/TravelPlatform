from PIL import Image, ImageFont, ImageDraw
import qrcode
from flask import current_app, send_from_directory, url_for
from .string_tools import get_rnd_filename_w_ext
import os
import random

def resize(image, path, width=200):
    img = Image.open(image)
    original_w, original_h = img.size
    if max(original_h, original_w) > width:
        if original_w > original_h:
            w = width
            h = int(w * original_h / original_w)
        else:
            h = width
            w = int(h * original_w / original_h)
        img = img.resize((w, h))#这里注意！必须要赋值！！！不是在原图操作，是返回操作成功的图片
    img.save(path)


#主要用于剪裁团队个人头像，不管图片多大都固定高度200
def resize_fix_height(image, path, height=200):
    img = Image.open(image)
    original_w, original_h = img.size
    width = int(original_w*height/original_h)
    img = img.resize((width, height))
    img.save(path)


def resize_fix_width(image, path, width=200):
    img = Image.open(image)
    original_w, original_h = img.size
    height = int(original_h*width/original_w)
    img = img.resize((width, height))
    img.save(path)


def cut(image, path, scale=0.5):
    img = Image.open(image)
    w, h = img.size
    if h/w > scale:
        h = w * scale
        img = img.crop((0, 0, w, h))
    img.save(path)


def get_qr():
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=1
    )
    return qr

def get_qrcode_filename():
    base_path = os.path.join(current_app.static_folder, 'images', 'qrcode')
    filename = get_rnd_filename_w_ext('test.jpg')
    filepath = os.path.join(base_path, filename)
    return filepath, filename


#接收URL字符串，保存为二维码，并返回生成的随机文件名
#所有二维码图片保存在/static/images/qrcode目录
def qrcode_img(url):
    qr = get_qr()
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image()
    filepath, filename = get_qrcode_filename()
    img.save(filepath, quanlity=60)
    return filename


#根据文件名，返回二维码图片的URL链接
def qrcode_url_string(filename):
    if filename:
        return url_for('static', filename='images/qrcode/' + filename)


#将二维码粘贴在path路径下的图片的右下角
def qrcode_cover(url, path):
    cover = Image.open(path)
    cover_w, cover_h = cover.size
    qr = get_qr()
    qr.add_data(url)
    qr.make(fit=True)
    qrcode = qr.make_image()
    qr_w, qr_h = qrcode.size
    height = qr_h * 2
    width = int(cover_w*height/cover_h)
    cover = cover.resize((width, height)) #resize返回新图片
    cover.paste(qrcode, (width-qr_w-30, height-qr_h-30)) #paste在原图操作
    filepath, filename = get_qrcode_filename()
    cover.save(filepath, quanlity=60)
    return filename


#验证码
def gene_verification_code():
    if current_app.config.get('DEBUG'):
        font_path = r'C:\Windows\Fonts\Arial.ttf'
    else:
        font_path = r'/urs/share/fonts/truetype/Arial.ttf'
    import string
    img = Image.new('RGBA', (70, 36), 'white')
    draw = ImageDraw.Draw(img)
    source = list(string.ascii_lowercase)
    for number in range(0,10):
        source.append(str(number))
    code = ''.join(random.sample(source, 4))
    font = ImageFont.truetype(font_path, 22)
    draw.text((10,5), code, fill='red', font=font)
    for x in range(0, 70, 5):
        for y in range(0, 36, 5):
            draw.point((x,y), fill=rndColor())
    return img


def rndColor():
    return (random.randint(64, 255), random.randint(64, 255), random.randint(64, 255))



