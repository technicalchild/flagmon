#!/usr/bin/env python

from flask import Flask, render_template, send_from_directory
from sqlalchemy import func, desc, distinct

from models import User, Flag
from db import session
from utils import flag_query, map_rows


app = Flask(__name__)

@app.route('/')
def index():
    users = session.query(
            User.userid,
            User.username,
            func.count(Flag.flagid).label('count')
        ).join(Flag).group_by(Flag.userid).order_by(func.lower(User.username))
    flags = flag_query().order_by(Flag.flagid.desc()).limit(5)
    count = session.query(func.count(distinct(Flag.flagid))).scalar()
    unique = session.query(func.count(distinct(Flag.md5sum))).scalar()
    return render_template('userlist.html', users=map_rows(users), flags=map_rows(flags), count=count, unique=unique)

@app.route('/user/<int:userid>')
@app.route('/user/<int:userid>/<page>')
def userflags(userid, page='1'):
    flags = map_rows(flag_query(Flag.userid==userid).order_by(Flag.flagid))
    pages = len(flags) // 200 + 1
    if page.isdigit():
        page = int(page)
        page = page if page <= pages else pages
        flags = flags[0 + 200 * (page - 1):200 * page]

    return render_template('userflags.html', userid=userid, flags=flags, pages=pages)

@app.route('/spammed')
def spammed():
    flags = flag_query() \
    .add_column(func.count(Flag.md5sum).label('count')) \
    .group_by(Flag.md5sum, User.username) \
    .having(func.count(Flag.md5sum) >= 10) \
    .order_by(desc('count'))
    return render_template('spammed.html', title='Spammed Flags', flags=map_rows(flags))

@app.route('/latest')
def latest():
    flags = flag_query().order_by(Flag.flagid.desc()).limit(200)
    return render_template('flaglist.html', title='Latest Flags', flags=map_rows(flags))

@app.route('/longflags')
def longflags():
    flags = flag_query(Flag.longflag==True).order_by(Flag.flagid)
    return render_template('flaglist.html', title='Long Flags', flags=map_rows(flags))

@app.route('/audioflags')
def audioflags():
    flags = flag_query(Flag.audio==True).order_by(Flag.flagid)
    return render_template('audioflags.html', title='Winamp Flags', flags=map_rows(flags))

@app.route('/audio/<int:flagid>')
def audio(flagid):
    flag = session.query(Flag).filter(Flag.flagid==flagid).first()
    return send_from_directory('./images/', flag.path.split('/')[-1], mimetype='audio/mpeg')


if __name__ == '__main__':
    app.run(debug=False)
