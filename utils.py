import subprocess
import os
import shutil
import re
import urllib

import requests

from db import session
from models import User, Flag

from settings import SA_COOKIE


flag_url = 'http://fi.somethingawful.com/flags/'
image_folder = './images/'
audio_working_folder = './audio/'


def flag_query(where=True):
    return session.query(
            Flag.flagid,
            Flag.path,
            Flag.created,
            User.username
        ).join(User).filter(where)

def map_rows(query):
    fields = [col['name'] for col in query.column_descriptions]
    return [dict(zip(fields, row)) for row in query.all()]

def get_flag(flagid):
    return session.query(Flag).filter(Flag.flagid==flagid).first()

def get_filename(flag):
    return flag.path.split('/')[-1]

def fetch_userid(username):
    user = session.query(User).filter(User.username==username).first()
    if user:
        return user.userid

    try:
        profile_url = 'https://forums.somethingawful.com/member.php?action=getinfo&username='
        response = requests.get(profile_url + urllib.parse.quote(username), cookies=SA_COOKIE)
    except:
        return 0

    if not response.ok: return 0
    match = re.search(r'userid=(\d+)', response.text)
    userid = match and int(match.groups()[0]) or 0

    session.merge(User(userid=userid, username=username))
    session.commit()
    return userid

def fetch_username(userid):
    user = session.query(User).filter(User.userid==userid).first()
    if user:
        return user.username

    profile_url = 'https://forums.somethingawful.com/member.php?action=getinfo&userid='
    response = requests.get(profile_url + str(userid), cookies=SA_COOKIE)
    if not response.ok: return
    match = re.search(r'<h3>About (.+)</h3>', response.text)
    username = match and match.groups()[0] or 'INVALID'

    session.merge(User(userid=userid, username=username))
    session.commit()
    return username

def download_flag(flag):
    response = requests.get(flag_url + flag.path, stream=True)
    if not response.ok:
        print('cannot save flag')
        return
    with open(image_folder + get_filename(flag), 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response

def md5sum(flag):
    md5_command = 'md5sum "{}"'.format(image_folder + get_filename(flag))
    md5sum, _ = subprocess.check_output(md5_command, shell=True).decode('utf-8').split('  ')

    flag.md5sum = md5sum

def longflag(flag):
    dimensions_command = 'convert "{}[0]" -format "%w %h" info:'.format(image_folder + get_filename(flag))
    width, height = 0, 0

    try:
        width, height = subprocess.check_output(dimensions_command, shell=True).decode('utf-8').split(' ')
    except subprocess.CalledProcessError:
        pass

    flag.longflag = (int(width) > 250) or (int(height) > 100)

def audioflag(flag):
    if not os.path.exists(audio_working_folder):
        os.makedirs(audio_working_folder)

    filename = get_filename(flag)
    duration = 0
    mp3_filepath = os.path.abspath(audio_working_folder + '/' + filename + '.mp3')
    mp3_command = 'soxi -V0 -D "{}"'.format(mp3_filepath)

    try:
        os.symlink(os.path.abspath(image_folder + '/' + filename), mp3_filepath)
        duration = float(subprocess.check_output(mp3_command, shell=True).decode('utf-8'))
    except subprocess.CalledProcessError:
        pass
    finally:
        os.unlink(mp3_filepath)

    if duration < 0.7:
        flag.audio = False
    else:
        flag.audio = True
        print(duration, filename)

def process_flag(flag):
    download_flag(flag)
    longflag(flag)
    audioflag(flag)
    md5sum(flag)

    session.merge(flag)
    session.commit()

def process_flags():
    for flag in session.query(Flag).filter(Flag.md5sum==None).all():
        process_flag(flag)
