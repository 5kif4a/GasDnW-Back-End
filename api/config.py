import os
from os.path import join, dirname

from dotenv import load_dotenv

import api.utils as utils

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

DEBUG = os.environ.get('DEBUG')
SECRET_KEY = os.environ.get("SECRET_KEY")

# Database settings
DATABASE_USER = os.environ.get("DATABASE_USER")
DATABASE_PASSWORD = os.environ.get("DATABASE_PASSWORD")
HOST = os.environ.get("HOST")
PORT = os.environ.get("PORT")
DATABASE_NAME = os.environ.get("DATABASE_NAME")

args = (DATABASE_USER, DATABASE_PASSWORD, HOST, PORT, DATABASE_NAME)
DATABASE_URL = 'mysql://{}:{}@{}:{}/{}'.format(*args)
SQLITE_URL = r'sqlite:///D:\PyCharm Projects\GasDnW\db.sqlite3'

PATH_TO_WKHTMLTOPDF = os.environ.get("PATH_TO_WKHTMLTOPDF")

cfg = {
    'DEBUG': DEBUG,
    'SECRET_KEY': SECRET_KEY,
    'SQLALCHEMY_DATABASE_URI': SQLITE_URL,
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'FLASK_ADMIN_SWATCH': 'simplex',
    'RESTFUL_JSON': {'cls': utils.Encoder}
}
