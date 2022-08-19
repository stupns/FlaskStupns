from flask import Flask
from app.routes import main_rout
from config import Config

app = Flask(__name__)
app.register_blueprint(main_rout)
app.config.from_object(Config)
