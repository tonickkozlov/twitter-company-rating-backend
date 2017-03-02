import json
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

def write_tweet(redis_client, account, tweet, tweet_score):
    ''' will write tweet data into db '''
    tweet_data = {
        'id': tweet.id,
        'text': tweet.text,
        'entities': json.dumps(tweet.entities),
    }

    pipe = redis_client.pipeline()
    pipe.multi()
    # keep on instance of a tweet list sorted by id, and another one - by score
    pipe.zadd('tweetsabout:{0}'.format(account), tweet_data['id'], tweet_data['id'])
    pipe.zadd('tweetscores:{0}'.format(account), tweet_score, tweet_data['id'])
    # TODO: do not store original tweets?
    pipe.hmset('tweet:{0}'.format(tweet_data['id']), tweet_data)
    pipe.execute()

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
