'''Retrieve tweets, embeddings, and save into a database'''

import basilica
import tweepy
from decouple import config
from .models import DB, Tweet, User

TWITTER_AUTH = tweepy.OAuthHandler(config('TWITTER_CONSUMER_KEY'),
                                   config('TWITTER_CONSUMER_SECRET'))
TWITTER_AUTH.set_access_token(config('TWITTER_ACCESS_TOKEN'),
                             config('TWITTER_ACCESS_TOKEN_SECRET'))
TWITTER = tweepy.API(TWITTER_AUTH)
BASILICA = basilica.Connection(config('BASILICA_KEY'))

#add more functions here
def twitter_to_db(twi_name, count=200, excl_reps=True, inc_retwt=False):
    '''
    Gets user and their (count) tweets from twitter user name
    And inputs them into database
    excl_reps = Exclude replies(default True)
    inc_retwt = Include retweets(default False)    
    EX: twitter_to_db('elonmusk')
    '''
    username = TWITTER.get_user(twi_name)
    tweets = username.timeline(count=count, exclude_replies=excl_reps, include_retweets=inc_retwt, tweet_mode='extended')
    db_user = User(id=username.id, name=username.screen_name, newest_tweet_id=tweets[0].id)
    for i in tweets:
        embedding = BASILICA.embed_sentence(i.full_text, model='twitter')
        db_tweet = Tweet(id=i.id, text=i.full_text[:500], embedding=embedding)
        DB.session.add(db_tweet)
        db_user.tweets.append(db_tweet)
    
    DB.session.add(db_user)
    DB.session.commit()

def clear_db():
    '''
    Drop all data from db.sqlite3 and create new
    '''
    DB.drop_all()
    DB.create_all()
