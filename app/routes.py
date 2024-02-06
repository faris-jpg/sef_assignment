from app import app
from flask import render_template

@app.route('/')



@app.route('/index')
def index():
    user = {'username': 'Faris'}

    return render_template('index.html', title='Home', user=user)

@app.route('/board')
def board():
    user = {'username': 'Faris'}
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]

    return render_template('board.html',
                            title='Discussion Board',
                              user=user,
                                posts=posts)