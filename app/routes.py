from app import app, db
from app.models import User, Post
from flask import render_template, flash, redirect, url_for, request
from app.forms import LoginForm, RegistrationForm, PostForm
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa
from urllib.parse import urlsplit



@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/index')
@login_required
def index():
    return render_template('index.html', title='Home')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/board', methods=['GET', 'POST'])
@login_required
def board():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.body.data, user_id=current_user.id,)
        db.session.add(post)
        db.session.commit()
        flash('Posted!')
        return redirect(url_for('board'))
    return render_template('board.html',
                            title='Discussion Board',
                                posts= db.session.scalars(sa.select(Post).order_by(sa.desc(Post.timestamp))).all(),
                                form = form)


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
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))

    return render_template('user.html', user=user, posts=db.session.scalars(sa.select(Post).where(user.id == Post.user_id)).all())