from app import app, db
from flask import render_template, flash, redirect, url_for, request
from app.forms import CastingsForm, ExtrusionForm, LoginForm, PostForm, RegistrationForm, EditProfileForm, EmptyForm, ResetPasswordRequestForm, ResetPasswordForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import Extrusion, User, Post, Casting
from werkzeug.urls import url_parse
from datetime import datetime
from app.email import send_password_reset_email

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('posted!')
        return redirect(url_for('index'))
    posts = current_user.followed_posts().all()
    return render_template('index.html', title='Home', user=user, form=form, posts=posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('invalid username or pw')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('registration complete')
        return redirect(url_for('login'))
    return render_template('register.html', title='register', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = [
        {'author': user, 'body': 'Test1'},
        {'author': user, 'body': 'Test2'}
    ]
    form = EmptyForm()
    return render_template('user.html', user=user, posts=posts, form=form)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        db.session.commit()
        flash('saved')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
    return render_template('edit_profile.html', title='edit profile', form=form)

@app.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('user {} not found'.format(username))
            return redirect(url_for('index'))
        elif user == current_user:
            flash('cant follow urself!')
            return redirect(url_for('index'))
        elif user != current_user:
            current_user.follow(user)
            db.session.commit()
            flash('you re following {}'.format(username))
            return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))

@app.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('user {} not found'.format(username))
            return redirect(url_for('index'))
        elif user == current_user:
            flash('cant unfollow urself!')
            return redirect(url_for('user', username=username))
        elif user != current_user:
            current_user.unfollow(user)
            db.session.commit()
            flash('unfollowed {}'.format(username))
            return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))

@app.route('/tasks')
@login_required
def tasks():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('posted!')
        return redirect(url_for('tasks'))
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('tasks.html', title='Tasks', user=user, form=form, posts=posts)

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('check email')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html', title='reset password', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()

@app.route('/castings', methods=['GET', 'POST'])
@login_required
def castings():
    casting_data = Casting.query.order_by(Casting.casting_no.asc()).all()
    return render_template('castings.html', title='castings', castings=casting_data)

@app.route('/new_casting', methods=['GET', 'POST'])
@login_required
def new_casting():
    form = CastingsForm()
    if form.validate_on_submit():
        casting = Casting(casting_no=form.casting_no.data, casting_date=form.casting_date.data, casting_composition=form.casting_composition.data)
        db.session.add(casting)
        db.session.commit()
        flash('casting added')
        return redirect(url_for('castings'))
    return render_template('new_casting.html', title='new casting', form=form, user=user)

@app.route('/extrusions', methods=['GET', 'POST'])
@login_required
def extrusion():
    form = ExtrusionForm()
    if form.validate_on_submit():
        extrusion = Extrusion(extrusion_no=form.extrusion_no.data, extrusion_composition=form.extrusion_composition.data)
        db.session.add(extrusion)
        db.session.commit()
        flash('extrusion added')
        return redirect(url_for('extrusion'))
    return render_template('extrusions.html', title='extrusions', form=form,  user=user)

@app.route('/dummy', methods=['GET', 'POST'])
@login_required
def dummy():
    casting_data = Casting.query.order_by(Casting.casting_no.asc()).all()
    extrusion_data = Extrusion.query.order_by(Extrusion.extrusion_no.asc()).all()
    return render_template('dummy.html', title='dummy', castings=casting_data, extrusions=extrusion_data)
