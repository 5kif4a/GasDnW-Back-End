from flask import Flask
from flask_admin import Admin
from flask_cors import CORS
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from flask_compress import Compress

from .config import cfg

app = Flask(__name__, template_folder='../templates', static_folder="../static")
app.config.from_mapping(cfg)

db = SQLAlchemy(app)  # SQLAlchemy
migrate = Migrate(app, db)  # Flask-Migrate

with app.app_context():
    if db.engine.url.drivername == 'sqlite':
        migrate.init_app(app, db, render_as_batch=True)
    else:
        migrate.init_app(app, db)


api = Api(app)  # Flask-RESTful
admin = Admin(app, template_mode='bootstrap3')  # Flask-Admin
CORS(app)  # Flask-CORS
mail = Mail(app)  # Flask-Mail
Compress(app)  # Flask-Compress


import api.views
import api.admin


@app.after_request
def after_request(response):
    response.headers.add('Accept-Ranges', 'bytes')
    return response

if __name__ == '__main__':
    app.run()
