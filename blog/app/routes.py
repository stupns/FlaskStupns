from flask import Blueprint, render_template, flash, redirect, url_for

from app.forms import LoginForm

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


@main_rout.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect(url_for('main_rout.index'))
    return render_template('login.html', title='Sign In', form=form)
