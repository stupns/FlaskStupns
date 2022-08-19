from flask import Flask
from app.routes import main_rout

app = Flask(__name__)
app.register_blueprint(main_rout)
