'''These are my database models'''

from flask_sqlalchemy import SQLAlchemy

# import database. Capital for global scope
DB = SQLAlchemy()


class User(DB.Model):
    '''Twitter users that we analyze'''
    id = DB.Column(DB.BigInteger, primary_key=True)
    name = DB.Column(DB.String(20), nullable=False)
    newest_tweet_id = DB.Column(DB.BigInteger)
    number_followers = DB.Column(DB.BigInteger)
    profile_image = DB.Column(DB.Unicode(500))


def __repr__(self):
    return '<User {}>'.format(self.name)


class Tweet(DB.Model):
    '''User's tweets from twitter'''
    id = DB.Column(DB.BigInteger, primary_key=True)
    text = DB.Column(DB.Unicode(500))
    user_id = DB.Column(DB.BigInteger, DB.ForeignKey('user.id'), nullable=False)
    user = DB.relationship('User', backref=DB.backref('tweets', lazy=True))

    embedding = DB.Column(DB.PickleType, nullable=False)


def __repr__(self):
    return '<Tweet {}>'.format(self.text)
