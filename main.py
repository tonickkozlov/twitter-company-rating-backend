import sys
import redis
from api import api
import db


if __name__ == '__main__':
    r = redis.StrictRedis(decode_responses=True)
    for company in db.get_companies(r):
        print('====================', company, '====================')
        best = db.get_best_tweets(r, company)
        worst = db.get_worst_tweets(r, company)
        print('==========', 'best', '==========')
        for (tweet_id, score) in best:
            print(tweet_id, db.get_tweet(r, tweet_id)['text'], score)
        print('==========', 'worst', '==========')
        for (tweet_id, score) in worst:
            print(tweet_id, db.get_tweet(r, tweet_id)['text'], score)

