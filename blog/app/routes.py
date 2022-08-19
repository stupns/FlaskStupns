from flask import Blueprint, render_template
main_rout = Blueprint('main_rout', __name__,
                      template_folder='templates',
                      static_folder='static')


@main_rout.route('/')
@main_rout.route('/index')
def index():
    user = {'username': 'Serhii'}
    posts = [
        {
            'author': {'username': 'Serhii'},
            'body': 'Beautiful day in Ukraine!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template('index.html', title='Home', user=user, posts=posts)
