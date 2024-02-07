from app import app, db, UPLOAD_FOLDER
from app.models import User, Post, File
from flask import render_template, flash, redirect, send_from_directory, url_for, request
from app.forms import LoginForm, RegistrationForm, PostForm, RoleForm, DeletePost, UploadForm, DeleteFile
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa
from urllib.parse import urlsplit
import os
from werkzeug.utils import secure_filename



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

@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.body.data, user_id=current_user.id,)
        db.session.add(post)
        db.session.commit()
        flash('Posted!')
        return redirect(url_for('index'))
    return render_template('index.html',
                            title='Discussion Board',
                                posts= db.session.scalars(sa.select(Post).order_by(sa.desc(Post.timestamp))).all(),
                                form = form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/board', methods=['GET', 'POST'])
@login_required
def board():
    form =  DeleteFile()
    if form.validate_on_submit():
        file = db.session.scalar(sa.select(File).where(form.file_ID == File.id))
        db.session.delete(file)
        db.session.commit()
        flash('Deleted!')

    return render_template('board.html',title='Upload', form=form, files=db.session.scalars(sa.select(File)).all())

@app.route('/adminboard', methods=['GET', 'POST'])
@login_required
def adminboard():
    if not current_user.is_admin():
        return redirect(url_for('index'))
    form = DeletePost()
    if form.validate_on_submit():
        post = db.session.scalar(sa.select(Post).where(form.post_ID.data == Post.id))
        # if post is None:
        #     flash('Please enter an existing post ID')
        #     return redirect(url_for('adminboard'))
        db.session.delete(post)
        db.session.commit()
        flash('Deleted!')
        return redirect(url_for('adminboard'))
    return render_template('adminboard.html',
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

@app.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    form = RoleForm()
    if form.validate_on_submit():
        user.set_role(int(form.role.data))
        db.session.commit()
    return render_template('user.html', user=user,form = form, posts=db.session.scalars(sa.select(Post).where(user.id == Post.user_id)).all())

@app.route('/list')
@login_required
def list():
    if not current_user.is_admin():
        flash('Not authorized to access this page')
        return redirect(url_for('userlist'))
    return render_template('list.html', title='User List', users = db.session.scalars(sa.select(User)).all())

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    form = UploadForm()
    
    if form.validate_on_submit():
        filename = secure_filename(form.file.data.filename)

        form.file.data.save('uploads/' + filename)
        file = File(filename=filename, user_id=current_user.id, path='uploads/' + filename, description=form.description.data)
        db.session.add(file)
        db.session.commit()
        flash('File uploaded!')

        return redirect(url_for('upload'))

    return render_template('upload.html',title='Upload', form=form)

@app.route('/listuploads')
def uploads():
    return render_template('listuploads.html', title='Uploads', files = db.session.scalars(sa.select(File)).all())
