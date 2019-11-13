'''Build app factory and do routes and configuration'''

from decouple import config
from flask import Flask, render_template, request
from .models import DB, User
from .twitter import add_or_update_user

#now we make a app factory

def create_app():
    app = Flask(__name__)

    #add our config
    app.config['SQLALCHEMY_DATABASE_URI'] = config('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    #now have the database know about the app
    DB.init_app(app)

    @app.route("/")
    def root():
        users = User.query.all()
        return render_template('base.html', title='Home', users=users)

    # Adding in new route to add or get users
    @app.route('/user', methods=['POST']) #uses form
    @app.route('/user/<name>', methods=['GET']) #needs paramater (<name>)
    def user(name=None, message=''):
        name = name or request.values['user_name']
        try:
            if request.method == 'POST':
                add_or_update_user(name)
                message = f'User {name} sucessfully added!'
            tweets = User.query.filter(User.name == name).one().tweets
        except Exception as e:
            message = f'Error adding {name}: {e}'
            tweets = []
        return render_template('user.html', title=name, tweets=tweets,
                               message=message)

    @app.route('/reset')
    def reset():
        DB.drop_all()
        DB.create_all()
        return render_template('base.html', title='Reset', users=[])
    return app
