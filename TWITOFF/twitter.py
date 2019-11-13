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


# Function to add users to the DB
def twitter_to_db(twi_name, count=200, excl_reps=True, inc_retwt=False):
    '''
    Gets user and their (count) tweets from twitter user name
    And inputs them into database
    excl_reps = Exclude replies(default True)
    inc_retwt = Include retweets(default False)
    EX: twitter_to_db('elonmusk')
    '''
    username = TWITTER.get_user(twi_name)
    tweets = username.timeline(count=count, exclude_replies=excl_reps,
                               include_retweets=inc_retwt,
                               tweet_mode='extended')
    db_user = User(id=username.id, name=username.screen_name,
                   newest_tweet_id=tweets[0].id,
                   number_followers=username.followers_count)
    for i in tweets:
        embedding = BASILICA.embed_sentence(i.full_text, model='twitter')
        db_tweet = Tweet(id=i.id, text=i.full_text[:500], embedding=embedding)
        DB.session.add(db_tweet)
        db_user.tweets.append(db_tweet)

    DB.session.add(db_user)
    DB.session.commit()


# Function to clear the DB and reset it
def clear_db():
    '''
    Drop all data from db.sqlite3 and create new
    '''
    DB.drop_all()
    DB.create_all()


def add_or_update_user(username):
    '''
    Add or update a user and their tweets, or else error
    '''
    try:
        twitter_user=TWITTER.get_user(username)
        db_user=(User.query.get(twitter_user.id) or
                 User(id=twitter_user.id, name=username))
        DB.session.add(db_user)
        tweets=twitter_user.timeline(count=200, exclude_replies=True,
                                     include_retweets=False,
                                     tweet_mode='extended',
                                     since_id=db_user.newest_tweet_id)
        if tweets:
            db_user.newest_tweet_id = tweets[0].id
        for tweet in tweets:
            embedding=BASILICA.embed_sentence(tweet.full_text, model='twitter')
            db_tweet=Tweet(id=tweet.id, text=tweet.full_text[:300],
                           embedding=embedding)
            db_user.tweets.append(db_tweet)
            DB.session.add(db_tweet)
    except Exception as e:
        print(f'Error processing {username}: {e}')
        raise e
    else:
        DB.session.commit()


# Function to add users to the DB without a for loop
# def improved(twi_name, count=200, excl_reps=True, inc_retwt=False):
#     '''
#     Same as twitter_to_db method but without a for loop(should be faster!)
#     Gets user and their (count) tweets from twitter user name
#     And inputs them into database
#     excl_reps = Exclude replies(default True)
#     inc_retwt = Include retweets(default False)
#     EX: twitter_to_db('elonmusk')
#     '''
#     username = TWITTER.get_user(twi_name)
#     tweets = username.timeline(count=count, exclude_replies=excl_reps,
#                                include_retweets=inc_retwt, tweet_mode='extended')
#     db_user = User(id=username.id, name=username.screen_name,
#                    newest_tweet_id=tweets[0].id,
#                    number_followers=username.followers_count)
#     embedding = BASILICA.embed_sentences(tweets.full_text, model='twitter')
#     # FIGURE OUT WHAT THIS DOES!db_user.tweets.extend()
