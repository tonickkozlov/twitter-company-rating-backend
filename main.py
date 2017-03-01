import sys
import random
import redis
import time
import tweepy
from api import api
from twitter_getter import get_tweets_by_company

# need no more than this in db
TWEETS_WANTED = 1000

def get_tweet_count(redis_client, company_name):
    ' will return count of tweets that exist in the db for ``company``'

    return redis_client.zcount('tweetsby:{0}'.format(company_name), 0, 'inf')


def get_max_tweet_id(redis_client, company_name):
    ' will return max id of a tweet about ``company`` in db'

    try:
        return int(redis_client.zrange('tweetsby:{0}'.format(company_name), 0, 0, desc=True)[0])
    except IndexError:
        return 0


if __name__ == '__main__':
    company_name = sys.argv[1].replace(' ', '').lower()

    r = redis.StrictRedis(decode_responses=True);

    print(company_name, get_tweet_count(r, company_name), get_max_tweet_id(r, company_name))

    tweets_limit = TWEETS_WANTED - get_tweet_count(r, company_name)
    since_id = get_max_tweet_id(r, company_name)

    print('will try to fetch {0} tweets for {1} starting from {2}'.format(tweets_limit, company_name, since_id))

    for tweet in get_tweets_by_company(api, company_name, since_id=since_id, limit=tweets_limit):
        print(company_name, tweet.id)
        r.sadd('companies', company_name)
        # use id as both score, and value
        r.zadd('tweetsby:{0}'.format(company_name), tweet.id, tweet.id)
        r.hmset('tweets:{0}'.format(tweet.id), dict(text=tweet.text, company=company_name, created_at=tweet.created_at.timestamp()))
