from itertools import cycle, islice
from math import inf

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

def sync_tweets(api, redis_client, account, limit=inf, max_tweets=inf):
    ''' will fetch max of `limit` tweets from Twitter mentioning `@account`,
    analyze them and write to db '''

    since_id = db.get_max_tweet_id(redis_client, account)
    print('Started syncing tweets mentioning ', account, 'starting from ', since_id)
    tweets_processed = 0
    for tweet in twitter.get_tweets_about_company(api, account, since_id=since_id):

        if tweets_processed >= limit:
            break

        score = get_sentiment_score(tweet.text, tweet.entities)

        if score == 0.0:
            continue

        with redis_client.pipeline() as pipe:
            pipe.watch('tweetsabout:{0}'.format(account))
            n_tweets = db.get_number_of_tweets(pipe, account)
            current_score = db.get_company_score(redis_client, account)

            tweets_to_remove = db.get_tweets_timeline(
                    pipe, account, 1, withscores=False
                    ) if n_tweets >= max_tweets else []

            removed_tweets_score = sum([db.get_tweet_score(pipe, account, tweet_id)
                for tweet_id in tweets_to_remove])

            pipe.multi()
            # batch-process insert operation
            db.write_tweet(pipe, account, tweet, score)
            db.remove_tweets(pipe, account, *tweets_to_remove)

            # sliding re-calculation of the score
            new_score = ((current_score * n_tweets - removed_tweets_score + score) /
                    (n_tweets + 1 - len(tweets_to_remove)))
            db.set_company_score(pipe, account, new_score)

            pipe.execute()

        tweets_processed += 1

        yield { 'account': account, 'tweet': tweet, 'score': score, 'removed': tweets_to_remove }
