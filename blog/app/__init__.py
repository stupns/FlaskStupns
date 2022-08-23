from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from app.routes import main_rout
from config import Config

app = Flask(__name__)
app.register_blueprint(main_rout)
app.config.from_object(Config)

db = SQLAlchemy(app)

login = LoginManager(app)
login.login_view = 'main_rout.login'
migrate = Migrate(app, db)

from app import models, routes
