from datetime import datetime, timezone
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5

class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True,
                                                unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True,
                                             unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))

    posts: so.WriteOnlyMapped['Post'] = so.relationship(
        back_populates='author')
    
    files: so.WriteOnlyMapped['File'] = so.relationship(
        back_populates='uploader')
    
    role: so.Mapped[int] = so.mapped_column(sa.Integer, default=-1, index=True, unique=False)

    assignments: so.WriteOnlyMapped['Assignment'] = so.relationship(
        back_populates='asmtauthor')
    
    submissions: so.WriteOnlyMapped['Submission'] = so.relationship(
        back_populates='submitter')


    def __repr__(self):
        return '<User {}>'.format(self.username)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'
    
    def set_role(self, role):
        self.role = role
        return
    
    def is_admin(self):
        return self.role == 0
    
    def is_lecturer(self):
        return self.role == 1

    def get_role(self):
        roles = {
            -1 : 'Unverified User',
            0 : 'Admin',
            1 : 'Lecturer',
            2 : 'Student'
        }
        return roles.get(self.role)


class Post(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    body: so.Mapped[str] = so.mapped_column(sa.String(140))
    timestamp: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc))
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id),
                                               index=True)

    author: so.Mapped[User] = so.relationship(back_populates='posts')

    def __repr__(self):
        return '<Post {}>'.format(self.body)
    
    def get_ftime(self):
        return self.timestamp.strftime("%H:%M %d/%m/%y")

class File(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    filename: so.Mapped[str] = so.mapped_column(sa.String(140))
    timestamp: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc))
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id),
                                               index=True)
    path: so.Mapped[str] = so.mapped_column(sa.String(140))

    uploader: so.Mapped[User] = so.relationship(back_populates='files') 

    description: so.Mapped[str] = so.mapped_column(sa.String(140), index=False, unique=False, nullable=True)

    title: so.Mapped[str] = so.mapped_column(sa.String(140), index=False, unique=False, nullable=True, default='Untitled')

    submissions: so.Mapped['Submission'] = so.relationship(back_populates='file')

    def __repr__(self):
        return f'<File {self.filename}> {self.title} {self.description} '
    
class Assignment(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    title: so.Mapped[str] = so.mapped_column(sa.String(140))
    description: so.Mapped[str] = so.mapped_column(sa.String(255))
    timestamp: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc))
    duedate: so.Mapped[datetime] = so.mapped_column(
        index=True, nullable=True)
    totalMarks: so.Mapped[float] = so.mapped_column(sa.Float, index=False, unique=False, nullable=True, default=0)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id),
                                               index=True)

    asmtauthor: so.Mapped[User] = so.relationship(back_populates='assignments')

    submissions: so.Mapped['Submission'] = so.relationship(back_populates='assignment')

    def __repr__(self):
        return f'<Assignment {self.title}> {self.description} '
    
class Submission(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    title: so.Mapped[str] = so.mapped_column(sa.String(140))
    description: so.Mapped[str] = so.mapped_column(sa.String(140))
    timestamp: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc))
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id),
                                               index=True)
    file_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(File.id),
                                               index=True)
    assignment_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Assignment.id),
                                               index=True)

    submitter: so.Mapped[User] = so.relationship(back_populates='submissions')

    assignment: so.Mapped[Assignment] = so.relationship(back_populates='submissions')

    file: so.Mapped[File] = so.relationship(back_populates='submissions')

    
    def __repr__(self):
        return f'<Submission {self.title}> {self.description} '

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))

