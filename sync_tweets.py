import db
import twitter
from twitter_rating import get_sentiment_score
from itertools import cycle, islice

def roundrobin(*iterables):
    "roundrobin('ABC', 'D', 'EF') --> A D E B F C"
    # Recipe credited to George Sakkis
    pending = len(iterables)
    nexts = cycle(iter(it).__next__ for it in iterables)
    while pending:
        try:
            for next in nexts:
                yield next()
        except StopIteration:
            pending -= 1
            nexts = cycle(islice(nexts, pending))

def sync_tweets(api, redis_client, account, limit=1000):
    ''' will fetch max of `limit` tweets from Twitter mentioning `@account`,
    analyze them and write to db '''

    since_id = db.get_max_tweet_id(redis_client, account)
    print('Started syncing tweets mentioning ', account, 'starting from ', since_id)
    for tweet in twitter.get_tweets_about_company(api, account, since_id=since_id, limit=limit):
        score = get_sentiment_score(tweet.text, tweet.entities)
        db.write_tweet(redis_client, account, tweet, score)
        yield { 'account': account, 'tweet': tweet, 'score': score }

    db.update_company_overall_score(redis_client, account)

if __name__ == '__main__':
    from api import api
    import redis

    r = redis.StrictRedis(decode_responses=True)
    companies = db.get_companies(r)


    sync_results = [sync_tweets(api, r, account) for account in companies]
    for result in roundrobin(*sync_results):
        print('============================================================')
        print('> account', result['account'])
        print('------------------------------')
        print(result['tweet'].text)
        print('------------------------------')
        print('> score', result['score'])
