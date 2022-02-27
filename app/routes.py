from app import app
from flask import render_template

@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Ryszard'}
    posts= [
        {
            'author': {'username': 'Kunka'},
            'body': 'Kosmos Colorado podbija Europe!'
        },
        {
            'author': {'username': 'Ryszard'},
            'body': 'Kosmos Colorado podbija Azje!'
        }
    ]
    return render_template('index.html', title='Home', user=user, posts=posts)

