#!/usr/bin/env python

import time

import requests
from sqlalchemy.sql import exists

from db import session
from models import User, Flag
from utils import fetch_userid, process_flag


def fetch_flag():
    flag_url = 'https://forums.somethingawful.com/flag.php?forumid=26'
    try:
        response = requests.get(flag_url)
    except:
        return
    if not response.ok: return
    flag = response.json()
    process_flag_json(flag)

def process_flag_json(flag):
    flag['raw'] = str(flag)
    flag['flagid'] = int(flag['path'].split('.')[0].split('/')[-1])
    flag['userid'] = fetch_userid(flag['username'])
    del flag['username']

    already_fetched = session.query(exists().where(Flag.flagid==flag['flagid'])).scalar()

    session.merge(Flag(**flag))
    session.commit()

    if not already_fetched:
        flag = session.query(Flag).filter(Flag.flagid==flag['flagid']).first()
        process_flag(flag)
        print(flag, session.query(User).count(), session.query(Flag).count())

if __name__ == '__main__':
    from special import load_special_users
    load_special_users()
    while True:
        fetch_flag()
        time.sleep(0.2)
