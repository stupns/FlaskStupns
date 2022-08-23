from datetime import datetime

from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

from app.forms import LoginForm, RegistrationForm, EditProfileForm, EmptyForm

main_rout = Blueprint('main_rout', __name__,
                      template_folder='templates',
                      static_folder='static')


@main_rout.route('/')
@main_rout.route('/index')
@login_required
def index():
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
    return render_template('index.html', title='Home', posts=posts)


@main_rout.route('/login', methods=['GET', 'POST'])
def login():
    from app.models import User
    if current_user.is_authenticated:
        return redirect(url_for('main_rout.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('main_rout.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main_rout.index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@main_rout.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main_rout.index'))


@main_rout.route('/register', methods=['GET', 'POST'])
def register():
    from app import db
    from app.models import User

    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('main_rout.login'))
    return render_template('register.html', title='Register', form=form)


@main_rout.route('/user/<username>')
@login_required
def user(username):
    from app.models import User

    user = User.query.filter_by(username=username).first_or_404()
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    form = EmptyForm()
    return render_template('user.html', user=user, posts=posts, form=form)


@main_rout.before_request
def before_request():
    from app import db
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@main_rout.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    from app import db

    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('main_rout.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)


@main_rout.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    from app import db
    from app.models import User

    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User {} not found.'.format(username))
            return redirect(url_for('main_rout.index'))
        if user == current_user:
            flash('You cannot follow yourself!')
            return redirect(url_for('main_rout.user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash('You are following {}!'.format(username))
        return redirect(url_for('main_rout.user', username=username))
    else:
        return redirect(url_for('main_rout.index'))


@main_rout.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    from app import db
    from app.models import User

    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User {} not found.'.format(username))
            return redirect(url_for('index'))
        if user == current_user:
            flash('You cannot unfollow yourself!')
            return redirect(url_for('user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash('You are not following {}.'.format(username))
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))
