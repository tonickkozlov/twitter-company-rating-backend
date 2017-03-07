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
        with redis_client.pipeline() as pipe:
            pipe.watch('tweetsabout:{0}'.format(account))
            n_tweets = db.get_number_of_tweets(pipe, account)

            tweets_to_remove = db.get_oldest_tweets(pipe, account, 1) if n_tweets >= limit else []

            pipe.multi()
            # batch-process insert operation
            db.write_tweet(pipe, account, tweet, score)
            db.remove_tweets(pipe, account, *tweets_to_remove)
            pipe.execute()
            yield { 'account': account, 'tweet': tweet, 'score': score, 'removed': tweets_to_remove }

    db.update_company_overall_score(redis_client, account)
    print('score updated for', account)

if __name__ == '__main__':
    from api import api
    import redis
    import sys

    r = redis.StrictRedis(decode_responses=True)
    # process all companies if params are not given
    companies = { sys.argv[1] } if len(sys.argv) > 1 else db.get_companies(r)

    sync_results = [sync_tweets(api, r, account) for account in companies]
    for result in roundrobin(*sync_results):
        print('============================================================')
        print('> account', result['account'])
        print('------------------------------')
        print(result['tweet'].id)
        print(result['tweet'].text.replace('\n', ''))
        print('------------------------------')
        print('> score', result['score'])
        print('> removed', result['removed'])
