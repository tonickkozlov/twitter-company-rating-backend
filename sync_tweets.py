import db
import twitter
from twitter_rating import get_sentiment_score

def sync_tweets(api, redis_client, account, limit=200):
    ''' will fetch max of `limit` tweets from Twitter mentioning `@account`,
    analyze them and write to db '''

    since_id = db.get_max_tweet_id(redis_client, account)
    print('since', since_id)
    for tweet in twitter.get_tweets_about_company(api, account, since_id=since_id, limit=limit):
        score = get_sentiment_score(tweet.text, tweet.entities)
        db.write_tweet(redis_client, account, tweet, score)
        print('==========', tweet.id, '==========');
        print(tweet.text, score)

if __name__ == '__main__':
    from api import api
    import redis

    r = redis.StrictRedis(decode_responses=True)
    companies = db.get_companies(r)
    for account in companies:
        sync_tweets(api, r, account)



