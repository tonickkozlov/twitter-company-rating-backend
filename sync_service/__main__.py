import sys
import redis
import fileinput
from itertools import chain
from random import sample

from lib.api import api
from lib import db

from .init_companies import add_company
from .sync_tweets import sync_tweets, roundrobin

N_TWEETS_PER_RUN=500
MAX_TWEETS=10000
N_COMPANIES_PER_RUN=10

def usage():
    print('Usage:\n'
            'python3 -m sync_service init companies.txt\n'
            'python3 -m sync_service sync')

if len(sys.argv) < 2:
    usage()

r = redis.StrictRedis(host='redis', decode_responses=True)

if sys.argv[1] == 'init':
    del sys.argv[1] # required for following fileinput

    for line in fileinput.input():
        company_name = line.strip()
        add_company(r, company_name)

elif sys.argv[1] == 'sync':
    # process all companies if params are not given
    companies = [ sys.argv[2] ] if len(sys.argv) > 2 else list(db.get_companies(r))

    sample(companies, N_COMPANIES_PER_RUN)

    sync_results = [sync_tweets(
        api,
        r,
        account,
        limit=N_TWEETS_PER_RUN,
        max_tweets=MAX_TWEETS
        )
        for account in companies ]

    for result in chain(*sync_results):
        print(result['account'], '+', result['tweet'].id, '-', result['removed'])
else:
    usage()

