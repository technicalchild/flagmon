from db import session
from models import User, Flag

# profile fetch fails with certain special characters, even with URL-encoding
def load_special_users():
    session.merge(User(userid=62448, username="ACRE & EQUAT"))
    session.merge(User(userid=94203, username="+2 Sword of Chutney"))
    session.commit()