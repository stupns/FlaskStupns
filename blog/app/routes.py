from flask import Blueprint
main_rout = Blueprint('main_rout', __name__)


@main_rout.route('/')
@main_rout.route('/index')
def index():
    return "Hello, World!"
