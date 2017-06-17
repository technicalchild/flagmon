#!/usr/bin/env python

import requests
from sqlalchemy import func
from sqlalchemy.sql import exists

from dateutil.parser import parse

from models import User, Flag
from db import session
from utils import fetch_username
from fetch import process_flag_json


def steal_flags():
    users_url = 'https://jims.bike/api/user'
    response = requests.get(users_url)
    if not response.ok: return
    items = response.json()
    userids = [x['id'] for x in items]

    users = session.query(
            User.userid,
            func.count(Flag.flagid)
        ).join(Flag).group_by(Flag.userid).all()

    for userid in set(userids) - set([x[0] for x in users]):
        fetch_username(userid)

    fetched_counts = {x['id']: x['flagCount'] for x in items}
    local_counts = {x[0]: x[1] for x in users}

    for userid, count in local_counts.items():
        if fetched_counts[userid] > count:
            print("im gay")

if __name__ == '__main__':
    from special import load_special_users
    load_special_users()
    steal_flags()
