from itertools import cycle, islice

from lib import db
from lib import twitter
from lib.twitter_rating import get_sentiment_score

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
