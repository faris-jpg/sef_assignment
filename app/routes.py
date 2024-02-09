from app import app, db
from app.models import User, Post, File, Assignment, Submission
from flask import render_template, flash, redirect, send_from_directory, url_for, request
from app.forms import LoginForm, RegistrationForm, PostForm, RoleForm, DeletePost, UploadForm, DeleteFile, UploadButton, AssignmentForm, MarksForm
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa
from datetime import datetime, timezone
from urllib.parse import urlsplit
import os
from werkzeug.utils import secure_filename


# Contributors:
#   Faris Imran bin Muhammmad Faisal - 1221304603



@app.route('/', methods=['GET', 'POST'])
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
    form = UploadButton()
    if form.validate_on_submit():
        return redirect(url_for('upload'))
    return render_template('board.html',title='Files', files=db.session.scalars(sa.select(File).where(File.submissions == None).order_by(sa.desc(File.timestamp))).all(), form=form)

@app.route('/details/<fileid>', methods=['GET', 'POST'])
@login_required
def details(fileid):
    
    file = db.session.scalar(sa.select(File).where(File.id == fileid))
    if file is None:
        flash('File not found')
        return redirect(url_for('board'))
    if file.submissions is not None:
        file.submissions.check_overdue()
        form = MarksForm()
        if form.validate_on_submit():
            submission = db.session.scalar(sa.select(Submission).where(Submission.file_id == fileid))
            submission.marks = form.marks.data
            db.session.commit()
            flash('Marks updated!')
            return redirect(url_for('details', fileid=fileid))
        return render_template('details.html', title='File Details', file=file, form=form)
    else:
        form = DeleteFile()
        if form.validate_on_submit():
            file = db.session.scalar(sa.select(File).where(fileid == File.id))
            db.session.delete(file)
            db.session.commit()
            flash('Deleted!')
            return redirect(url_for('board'))
        return render_template('details.html', title='File Details', file=file, form=form)
        
    
@app.route('/adminboard', methods=['GET', 'POST'])
@login_required
def adminboard():
    if not current_user.is_admin():
        return redirect(url_for('index'))
    form = DeletePost()
    if form.validate_on_submit():
        post = db.session.scalar(sa.select(Post).where(form.post_ID.data == Post.id))
        if post is None:
            flash('Please enter an existing post ID')
            return redirect(url_for('adminboard'))
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
    return render_template('user.html', 
                             user=user,
                              form = form,
                               posts=db.session.scalars(sa.select(Post).where(user.id == Post.user_id)).all())

@app.route('/list')
@login_required
def list():
    if not current_user.is_admin():
        flash('Not authorized to access this page')
        return redirect(url_for('userlist'))
    return render_template('list.html', title='User List',
                            users = db.session.scalars(sa.select(User)).all())

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = UploadForm()
    
    if form.validate_on_submit():
        filename = secure_filename(form.file.data.filename)
        matchingname = db.session.scalar(sa.select(File).where(File.filename == filename))
        if matchingname is not None:
            flash('File with the same name already exists')
            return redirect(url_for('upload'))
        form.file.data.save('uploads/' + filename)
        file = File(filename=filename,
                    title = form.title.data,
                      user_id=current_user.id,
                        path='uploads/' + filename,
                          description=form.description.data)
        db.session.add(file)
        db.session.commit()
        flash('File uploaded!')

        return redirect(url_for('upload'))

    return render_template('upload.html',title='Upload', form=form)

@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/assignments', methods=['GET', 'POST'])
@login_required
def assignments():
    form = UploadButton()
    if form.validate_on_submit():
        return redirect(url_for('createAssignment'))
    return render_template('assignments.html',
                            title='Assignments',
                              assignments=db.session.scalars(sa.select(Assignment).order_by(sa.desc(Assignment.timestamp))).all(),
                                form=form)

@app.route('/detailsAssignment/<assignmentid>', methods=['GET', 'POST'])
@login_required
def detailsAssignment(assignmentid):
    form = UploadForm()
    assignment = db.session.scalar(sa.select(Assignment).where(Assignment.id == assignmentid))
    submittedFile = None
    if assignment is None:
        flash('Assignment not found')
        return redirect(url_for('assignments'))
    
    if current_user.is_student():
        submission = db.session.scalar(sa.select(Submission).where(Submission.assignment_id == assignmentid, Submission.user_id == current_user.id))
        if submission is not None:
            submittedFile = db.session.scalar(sa.select(File).where(File.id == submission.file_id))
    
    if current_user.is_admin() or current_user.is_lecturer():
        submittedFile = db.session.scalars(sa.select(File).where(File.submissions.has(Submission.assignment_id == assignmentid))).all()
    
    if form.validate_on_submit():
        filename = secure_filename(form.file.data.filename)
        matchingname = db.session.scalar(sa.select(File).where(File.filename == filename))
        if matchingname is not None:
            flash('File with the same name already exists')
            return redirect(url_for('detailsAssignment', assignmentid=assignmentid))
        
        form.file.data.save('uploads/' + filename)
        file = File(filename=filename,
                    title = form.title.data,
                      user_id=current_user.id,
                        path='uploads/' + filename,
                          description=form.description.data,
                            timestamp=datetime.now(timezone.utc))
        db.session.add(file)
        db.session.commit()
        flash('File uploaded!')
        submission = Submission(title=form.title.data,
                                 description=form.description.data,
                                   user_id=current_user.id,
                                     file_id=file.id,
                                       assignment_id=assignmentid,
                                         timestamp=datetime.now(timezone.utc))
        db.session.add(submission)
        db.session.commit()
        flash('Submitted!')
        return redirect(url_for('detailsAssignment', assignmentid=assignmentid))
    return render_template('detailsAssignment.html', title='Assignment Details', assignment=assignment, form=form, submittedFile=submittedFile)

@app.route('/createAssignment', methods=['GET', 'POST'])
@login_required
def createAssignment():
    form = AssignmentForm()
    if form.validate_on_submit():
        assignment = Assignment(title=form.title.data,
                                 description=form.description.data,
                                   user_id=current_user.id,
                                     duedate=form.duration.data,
                                       totalMarks=form.marks.data
        )
        db.session.add(assignment)
        db.session.commit()
        flash('Assignment created!')
        return redirect(url_for('assignments'))

    return render_template('createAssignment.html',title='Create Assignment', form=form)