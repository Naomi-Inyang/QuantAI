from ..constants import *

class Config(object):
    SECRET_KEY = APP_SECRET_KEY
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
