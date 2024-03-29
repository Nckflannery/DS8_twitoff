'''Build app factory and do routes and configuration'''

from decouple import config
from dotenv import load_dotenv
from flask import Flask, render_template, request
from .models import DB, User
from .predict import predict_user, lgbm_predict_user
from .twitter import improved

# Load dotenv
load_dotenv()


def create_app():
    app = Flask(__name__)

    # add our config
    app.config['SQLALCHEMY_DATABASE_URI'] = config('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # now have the database know about the app
    DB.init_app(app)

    @app.route("/")
    def root():
        users = User.query.all()
        return render_template('base.html', title='Home', users=users)

    # Adding in new route to add or get users
    @app.route('/user', methods=['POST'])  # uses form
    @app.route('/user/<name>', methods=['GET'])  # needs paramater (<name>)
    def user(name=None, message=''):
        name = name or request.values['user_name']
        try:
            if request.method == 'POST':
                improved(name)
                message = f'User {name} sucessfully added!'
            tweets = User.query.filter(User.name == name).one().tweets
        except Exception as e:
            message = f'Error adding {name}: {e}'
            tweets = []
        return render_template('user.html', title=name, tweets=tweets,
                               message=message)

    # adding in a route for predictions
    @app.route('/compare', methods=['POST'])
    def compare(message=''):
        user1, user2 = sorted([request.values['user1'],
                               request.values['user2']])
        if user1 == user2:
            message = 'Cannot compare a user to themselves'
        else:
            prediction = predict_user(user1, user2,
                                      request.values['tweet_text'])
            message = '{} is more likely to be said by {} than {}'.format(
                request.values['tweet_text'], user1 if prediction else user2,
                user2 if prediction else user1)
        return render_template('prediction.html', title='Prediction',
                               message=message)

    @app.route('/reset')
    def reset():
        DB.drop_all()
        DB.create_all()
        return render_template('base.html', title='Reset', users=[])
    return app
