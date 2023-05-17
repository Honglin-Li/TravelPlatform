from pypinyin import lazy_pinyin
from werkzeug.utils import secure_filename
import hashlib
import time
import bleach
import datetime
import random
import os


def get_md5_filename(name):
    return hashlib.md5((name + str(time.time())).encode('utf8')).hexdigest()[:15]


def get_md5_filename_w_ext(name, file):
    return get_md5_filename(name) + '.' + file.split('.')[1]


def get_filename_w_ext(name, file):
    return name + '.' + file.split('.')[1]


def get_rnd_filename():
    filename_prefix = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    return '%s%s' % (filename_prefix, str(random.randrange(1000, 10000)))


def get_rnd_filename_w_ext(filename):
    f_name, f_ext = os.path.splitext(filename)
    return get_rnd_filename() + f_ext


def trans_html(text):
    allow_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol',
                  'pre', 'strong', 'ul', 'h1', 'h2', 'h3', 'h4', 'p', 'span', 'table', 'thead',
                  'img', 'tbody', 'td', 'tr', 'cite', 'big', 'small', 'kbd', 'tt', 'del', 'samp']
    attrs = {'*': ['class', 'style', 'border'],
             'th': ['scope'],
             'a': ['href', 'rel'],
             'img': ['alt', 'src'],
             'table': ['cellpadding', 'cellspacing']}
    return bleach.linkify(
        bleach.clean(text=text, tags=allow_tags, attributes=attrs, strip=True)
    )
