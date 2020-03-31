import os
from os.path import join, dirname
from dotenv import load_dotenv

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
SQLITE_URL = 'sqlite:///db.sqlite3'

cfg = {
    'DEBUG': DEBUG,
    'SECRET_KEY': SECRET_KEY
}
