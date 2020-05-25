import os
from os.path import join, dirname

from dotenv import load_dotenv

import api.utils as utils

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

DEBUG = os.environ.get('DEBUG')
SECRET_KEY = os.environ.get("SECRET_KEY")
CLIENT_APP_BASE_URL = os.environ.get("CLIENT_APP_BASE_URL")

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

MAIL_SERVER = os.environ.get("MAIL_SERVER")
MAIL_PORT = os.environ.get("MAIL_PORT")
MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS")
MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER")
MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")

DER_BASE64_ENCODED_PRIVATE_KEY_FILE_PATH = os.path.join(os.getcwd(), "private_key.pem")
DER_BASE64_ENCODED_PUBLIC_KEY_FILE_PATH = os.path.join(os.getcwd(), "public_key.pem")

VAPID_PRIVATE_KEY = open(DER_BASE64_ENCODED_PRIVATE_KEY_FILE_PATH, "r+").read().strip("\n")
VAPID_PUBLIC_KEY = open(DER_BASE64_ENCODED_PUBLIC_KEY_FILE_PATH, "r+").read().strip("\n")

VAPID_CLAIMS = {
    "sub": "mailto:hy6ac777@mail.ru"
}

cfg = {
    'DEBUG': DEBUG,
    'SECRET_KEY': SECRET_KEY,
    'SQLALCHEMY_DATABASE_URI': SQLITE_URL,
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'FLASK_ADMIN_SWATCH': 'simplex',
    'RESTFUL_JSON': {'cls': utils.Encoder},
    'MAIL_SERVER': MAIL_SERVER,
    'MAIL_PORT': MAIL_PORT,
    'MAIL_USE_TLS': MAIL_USE_TLS,
    'MAIL_DEFAULT_SENDER': MAIL_DEFAULT_SENDER,
    'MAIL_USERNAME': MAIL_USERNAME,
    'MAIL_PASSWORD': MAIL_PASSWORD
}
