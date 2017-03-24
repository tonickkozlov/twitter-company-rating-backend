import json
from statistics import mean
''' Holds all necessary functions to access the database '''

def check_account_exists(db_function):
    ''' decorator that will raise a KeyError if a company does not exist '''
    def wrapper(redis_client, account, *args, **kwargs):
        if not redis_client.sismember('companies', account):
            raise KeyError('company "{0}" does not exist'.format(account))
        return db_function(redis_client, account, *args, **kwargs)

    return wrapper

def write_company(redis_client, company):
    ''' will write company data into the db '''
    company_data = {
        'name': company.name,
        'account': company.screen_name,
        'profile_image_url': company.profile_image_url
    }
    # init transaction
    pipe = redis_client.pipeline()
    pipe.multi()
    pipe.hmset('company:{0}'.format(company_data['account']), company_data)
    pipe.sadd('companies', company_data['account'])
    pipe.execute()

def get_companies(redis_client):
    ''' will get all companies '''
    return redis_client.smembers('companies')

@check_account_exists
def get_company_details(redis_client, account):
    ''' will get details for a given company '''
    keys = ['account', 'profile_image_url', 'name']
    values = redis_client.hmget('company:{0}'.format(account), *keys)
    return dict(zip(keys, values))

@check_account_exists
def get_company_score(redis_client, account):
    ''' will get company score from db '''
    return float(redis_client.get('companyscore:{0}'.format(account)) or 0)

@check_account_exists
def set_company_score(redis_client, account, score):
    ''' will get company score from db '''
    return redis_client.set('companyscore:{0}'.format(account), score)

@check_account_exists
def get_company_overall_score(redis_client, account):
    ''' will re-calculate average score for company at `account` '''
    ranges = redis_client.zrangebyscore('tweetscores:{0}'.format(account), min='-inf', max='inf', withscores=True)
    # count only non-neutral elements
    scores = [score[1] for score in ranges if score[1] != 0]
    average_score = mean(scores)
    return average_score

@check_account_exists
def update_company_overall_score(redis_client, account):
    score = get_company_overall_score(redis_client, account)
    redis_client.set('companyscore:{0}'.format(account), score)

@check_account_exists
def get_best_tweets(redis_client, account, limit=10):
    return redis_client.zrevrangebyscore('tweetscores:{0}'.format(account), 'inf', 0, withscores=True, start=0, num=limit)

@check_account_exists
def get_worst_tweets(redis_client, account, limit=10):
    return redis_client.zrangebyscore('tweetscores:{0}'.format(account), '-inf', 0, withscores=True, start=0, num=limit)

@check_account_exists
def get_number_of_tweets(redis_client, account):
    ''' will return number of tweets that's stored and mention `account` '''
    return redis_client.zcount('tweetsabout:{0}'.format(account), '-inf', 'inf')

@check_account_exists
def get_tweets_timeline(redis_client, account, limit=None, withscores=True):
    ''' will get ids of tweets in their creation order '''
    limiting_params = { 'start': 0, 'num': limit } if limit else {}
    return redis_client.zrangebyscore('tweetsabout:{0}'.format(account), '-inf', 'inf', withscores=withscores, **limiting_params)

@check_account_exists
def remove_tweets(redis_client, account, *tweets):
    if len(tweets) == 0:
        return

    redis_client.zrem('tweetsabout:{0}'.format(account), *tweets)
    redis_client.zrem('tweetscores:{0}'.format(account), *tweets)

@check_account_exists
def write_tweet(redis_client, account, tweet, tweet_score):
    ''' will write tweet data into db
        if `remove_oldest` is set, will erase the olders tweet '''

    tweet_data = {
        'id': tweet.id
    }

    # keep on instance of a tweet list sorted by id, and another one - by score
    redis_client.zadd('tweetsabout:{0}'.format(account), tweet_data['id'], tweet_data['id'])
    redis_client.zadd('tweetscores:{0}'.format(account), tweet_score, tweet_data['id'])

@check_account_exists
def get_tweet_score(redis_client, account, tweet_id):
    return redis_client.zscore('tweetscores:{0}'.format(account), tweet_id)

@check_account_exists
def get_max_tweet_id(redis_client, account):
    ' will return max id of a tweet about ``company`` in db'

    key_name = 'tweetsabout:{0}'.format(account)
    try:
        return int(redis_client.zrange(key_name, 0, 0, desc=True)[0])
    except IndexError:
        return 0

if __name__ == '__main__':
    import sys
    import redis
    r = redis.StrictRedis()
    update_company_overall_score(r, sys.argv[1])

