#!/usr/bin/env python

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import ForeignKey
from sqlalchemy import Boolean
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Flag(Base):
    __tablename__ = 'flags'

    flagid = Column(Integer, primary_key=True)
    raw = Column(String(255), nullable=False)
    userid = Column('userid', Integer, ForeignKey('users.userid'), nullable=False)
    path = Column(String(255), nullable=False)
    created = Column(String(10), nullable=False)
    md5sum = Column(String(32))
    longflag = Column(Boolean)
    audio = Column(Boolean)

class User(Base):
    __tablename__ = 'users'

    userid = Column(Integer, primary_key=True)
    username = Column(String(255), nullable=False)


if __name__ == '__main__':
    from sqlalchemy import create_engine
    from settings import DB_URI
    engine = create_engine(DB_URI)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
