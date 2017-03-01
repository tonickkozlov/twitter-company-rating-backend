import tweepy
import time
import sys
import random

''' Twitter API helpers (via tweepy) '''
def get_cursored_data(endpoint, *args, **kwargs):
    ' will get a generator for given api endpoint, will respect and retry on rate limiting'

    if 'limit' in kwargs and kwargs['limit'] == 0:
        return

    c = tweepy.Cursor(endpoint, *args, **kwargs).items(kwargs.get('limit'))

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


def guess_company_account(api, company_name):
    ' will get company twitter account name based on company name'
    g = get_cursored_data(api.search_users, q=company_name, limit=10)
    # get just the first result
    account = next(g)
    return account.screen_name


def get_tweets_by_company(api, company_name, since_id=0, limit=1000, **kwargs):
    ' will give out tweets for ``company_name`` starting with ``since_id``, and will give out max of ``limit`` results'
    return get_cursored_data(api.search,
            q='@{0}'.format(company_name),
            since_id=since_id,
            limit=limit,
            include_entities=True,
            **kwargs)
