'''These are my database models'''

from flask_sqlalchemy import SQLAlchemy

# import database. Capital for global scope
DB = SQLAlchemy()

class User(DB.Model):
    '''Twitter users that we analyze'''
    id = DB.Column(DB.Integer, primary_key=True)
    name = DB.Column(DB.String(20), nullable=False)

class Tweet(DB.Model):
    '''User's tweets from twitter'''
    id = DB.Column(DB.Integer, primary_key=True)
    text = DB.Column(DB.Unicode(280))