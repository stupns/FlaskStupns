import smtplib
import ssl
from datetime import datetime
from flask_mail import Message

from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

from app.forms import LoginForm, RegistrationForm, EditProfileForm, EmptyForm, PostForm, ResetPasswordRequestForm, \
    ResetPasswordForm
from app.email import send_password_reset_email
from config import Config

main_rout = Blueprint('main_rout', __name__,
                      template_folder='templates',
                      static_folder='static')


# region index
@main_rout.route('/', methods=['GET', 'POST'])
@main_rout.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    from app import app
    from app import db
    from app.models import Post

    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('main_rout.index'))
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main_rout.index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main_rout.index', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title='Home', form=form,
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)


# endregion
# region login
@main_rout.route('/login', methods=['GET', 'POST'])
def login():
    from app.models import User

    # Визначити, чи підтверджений цей користувач, і повернутися на домашню сторінку, якщо він підтверджений.
    if current_user.is_authenticated:
        return redirect(url_for('main_rout.index'))

    form = LoginForm()
    # Перевірка даних таблиці
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
    return render_template('/auth/login.html', title='Sign In', form=form)


# endregion
# region logout
@main_rout.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main_rout.index'))


# endregion
# region register
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


# endregion
# region user
@main_rout.route('/user/<username>')
@login_required
def user(username):
    from app import app
    from app.models import User
    from app.models import Post

    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    form = EmptyForm()
    return render_template('user.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url, form=form)


# endregion
# region profile
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


# endregion
# region follow
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


# endregion
# region unfollow
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
            return redirect(url_for('main_rout.index'))
        if user == current_user:
            flash('You cannot unfollow yourself!')
            return redirect(url_for('main_rout.user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash('You are not following {}.'.format(username))
        return redirect(url_for('main_rout.user', username=username))
    else:
        return redirect(url_for('main_rout.index'))


# endregion
# region explore
@main_rout.route('/explore')
@login_required
def explore():
    from app.models import Post
    from app import app

    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main_rout.explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main_rout.explore', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template("index.html", title='Explore', posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


# endregion
# region reset_password
@main_rout.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    from app.models import User

    if current_user.is_authenticated:
        return redirect(url_for('main_rout.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('main_rout.login'))
    return render_template('/auth/reset_password_request.html',
                           title='Reset Password', form=form)


# endregion
# region reset_password_token
@main_rout.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    from app.models import User
    from app import db
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)


# endregion

@main_rout.route('/test')
def new_func():
    context = ssl.create_default_context()
    with smtplib.SMTP("smtp.mailtrap.io", port=2525) as connection:
        connection.ehlo()
        connection.starttls(context=context)
        connection.ehlo()
        connection.login(
            user=Config.MAIL_USERNAME,
            password=Config.MAIL_PASSWORD
        )
        connection.sendmail(
            from_addr=Config.ADMINS[0],
            to_addrs='your-email@example.com',
            msg=f"Subject:Text\n\n"
                f"Body of the text"
        )


@main_rout.before_request
def before_request():
    from app import db
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
