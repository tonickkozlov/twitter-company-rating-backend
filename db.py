import json
from statistics import mean
''' Holds all necessary functions to access the database '''

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


def get_company_overall_score(redis_client, account):
    ''' will re-calculate average score for company at `account` '''
    ranges = redis_client.zrangebyscore('tweetscores:{0}'.format(account), min='-inf', max='inf', withscores=True)
    # count only non-neutral elements
    scores = [score[1] for score in ranges if score[1] != 0]
    average_score = mean(scores)
    return average_score

def update_company_overall_score(redis_client, account):
    score = get_company_overall_score(redis_client, account)
    redis_client.set('companyscore:{0}'.format(account), score)

def get_best_tweets(redis_client, account, limit=10):
    return redis_client.zrevrangebyscore('tweetscores:{0}'.format(account), 'inf', '-inf', withscores=True, start=0, num=limit)

def get_worst_tweets(redis_client, account, limit=10):
    return redis_client.zrangebyscore('tweetscores:{0}'.format(account), '-inf', 'inf', withscores=True, start=0, num=limit)

def get_number_of_tweets(redis_client, account):
    ''' will return number of tweets that's stored and mention `account` '''
    return redis_client.zcount('tweetsabout:{0}'.format(account), '-inf', 'inf')

def get_oldest_tweets(redis_client, account, num=1):
    ''' will return ids of oldest tweets '''
    return redis_client.zrangebyscore('tweetsabout:{0}'.format(account), '-inf', 'inf', start=0, num=num)

def remove_tweets(redis_client, account, *tweets):
    if len(tweets) == 0:
        return

    redis_client.zrem('tweetsabout:{0}'.format(account), *tweets)
    redis_client.zrem('tweetscores:{0}'.format(account), *tweets)

def write_tweet(redis_client, account, tweet, tweet_score):
    ''' will write tweet data into db
        if `remove_oldest` is set, will erase the olders tweet '''

    tweet_data = {
        'id': tweet.id,
        'text': tweet.text,
        'entities': json.dumps(tweet.entities),
    }

    # keep on instance of a tweet list sorted by id, and another one - by score
    redis_client.zadd('tweetsabout:{0}'.format(account), tweet_data['id'], tweet_data['id'])
    redis_client.zadd('tweetscores:{0}'.format(account), tweet_score, tweet_data['id'])
    # TODO: do not store original tweets?
    redis_client.hmset('tweet:{0}'.format(tweet_data['id']), tweet_data)

def get_tweet(redis_client, tweet_id):
    fields = ['id', 'text']
    id, text = redis_client.hmget('tweet:{0}'.format(tweet_id), fields)
    return {'id': id, 'text': text} 

def get_tweet_count(redis_client, account):
    ' will return count of tweets that exist in the db for ``company``'

    return redis_client.zcount('tweetsby:{0}'.format(account), 0, 'inf')

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

