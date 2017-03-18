import tweepy
import time
import sys
import random
from nltk.metrics.distance import edit_distance

''' Twitter API helpers (via tweepy) '''
def get_cursored_data(endpoint, *args, **kwargs):
    ' will get a generator for given api endpoint, will respect and retry on rate limiting'

    limit = kwargs.get('limit')
    if limit == 0:
        return

    c = tweepy.Cursor(endpoint, *args, **kwargs)
    c = c.items(limit) if limit else c.items() 

    while True:
        try:
            tweet = c.next()
            yield tweet
        except tweepy.TweepError:
            print('going to sleep for {0}'.format(kwargs.get('q')), file=sys.stderr)
            time.sleep(60 * random.randint(10, 20))
            continue
        except StopIteration:
            break


def get_tweets_about_company(api, account, since_id=0, limit=1000, **kwargs):
    ' will give out tweets for ``account`` starting with ``since_id``, and will give out max of ``limit`` results'
    tweets_processed = 0
    for tweet in (get_cursored_data(api.search,
            q='@{0}'.format(account),
            since_id=since_id,
            # limit=limit,
            include_entities=True,
            lang='en',
            **kwargs)):
        if tweets_processed >= limit:
            break
        if not tweet.retweeted and not tweet.text.startswith('RT '):
            yield tweet
            tweets_processed += 1


def get_company_account(api, company_name):
    ' will return company object from twitter by performin a search on `company_name` '
    cursor = get_cursored_data(api.search_users, q=company_name, limit=10)
    # block to fetch all companies
    candidates = [company for company in cursor]

    # if finding a perfect match failed - ask user for best choice,
    # provide assistance with edit distance
    edit_distances = [edit_distance(company_name.lower(), candidate.screen_name.lower()) for candidate in candidates]
    default_answer = edit_distances.index(min(edit_distances))

    return candidates[default_answer]


if __name__ == '__main__':
    from api import api
    t = get_tweets_about_company(api, 'microsoft')
    tweet = next(t)
    print(tweet.text)
