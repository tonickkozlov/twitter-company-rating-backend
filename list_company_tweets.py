''' prints number of tweets for all the companies '''

import redis
import main

r = redis.StrictRedis(decode_responses=True)

for company in r.smembers('companies'):
    print(company, main.get_tweet_count(r, company))
