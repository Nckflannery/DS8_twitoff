'''Prediction of users based on tweet embeddings'''

from lightgbm import LGBMRegressor
import numpy as np
import pickle
from sklearn.linear_model import LogisticRegression
from .models import User
from .twitter import BASILICA

def predict_user(user1_name, user2_name, tweet_text, cache=None):
    '''Determine and return which user is more likely to tweet given phrase'''
    user_set = pickle.dumps((user1_name, user2_name))
    if cache and cach.exists(user_set):
        log_reg = pickle.loads(cache.get(user_set))
    else:
        # get the users
        user1 = User.query.filter(User.name == user1_name).one()
        user2 = User.query.filter(User.name == user2_name).one()
        # get the embedding for the tweets of those user_set
        user1_embeddings = np.array([tweet.embedding for tweet in user1.tweets])
        user2_embeddings = np.array([tweet.embedding for tweet in user2.tweets])
        # split those into an array
        embeddings = np.vstack([user1_embeddings, user2_embeddings])
        labels = np.concatenate([np.ones(len(user1.tweets)),
                                 np.zeros(len(user2.tweets))])
        # Fit model
        log_reg = LogisticRegression(solver='lbfgs').fit(embeddings, labels)
        cache and cache.set(user_set, pickle.dumps(log_reg))
    tweet_embedding = BASILICA.embed_sentence(tweet_text, model='twitter')
    return log_reg.predict(np.array(tweet_embedding).reshape(1, -1))

# Let's try a new prediction with lightgbm regression
def lgbm_predict_user(user1_name, user2_name, tweet_text, cache=None):
    '''Determine and return which user is more likely to tweet given phrase'''
    user_set = pickle.dumps((user1_name, user2_name))
    if cache and cach.exists(user_set):
        log_reg = pickle.loads(cache.get(user_set))
    else:
        # get the users
        user1 = User.query.filter(User.name == user1_name).one()
        user2 = User.query.filter(User.name == user2_name).one()
        # get the embedding for the tweets of those user_set
        user1_embeddings = np.array([tweet.embedding for tweet in user1.tweets])
        user2_embeddings = np.array([tweet.embedding for tweet in user2.tweets])
        # split those into an array
        embeddings = np.vstack([user1_embeddings, user2_embeddings])
        labels = np.concatenate([np.ones(len(user1.tweets)),
                                 np.zeros(len(user2.tweets))])
        # Fit model
        lgbm_reg = LGBMRegressor(n_estimators=200).fit(embeddings, labels)
        cache and cache.set(user_set, pickle.dumps(log_reg))
    tweet_embedding = BASILICA.embed_sentence(tweet_text, model='twitter')
    return lgbm_reg.predict(np.array(tweet_embedding).reshape(1, -1))
