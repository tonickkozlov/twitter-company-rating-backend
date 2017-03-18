import sys
import redis
import fileinput
from itertools import chain

from lib.api import api
from lib import db

from .init_companies import add_company
from .sync_tweets import sync_tweets, roundrobin

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
    companies = { sys.argv[2] } if len(sys.argv) > 2 else db.get_companies(r)

    sync_results = [sync_tweets(api, r, account) for account in companies]

    for result in chain(*sync_results):
        print('============================================================')
        print('> account', result['account'])
        print('------------------------------')
        print(result['tweet'].id)
        print(result['tweet'].text.replace('\n', ''))
        print('------------------------------')
        print('> score', result['score'])
        print('> removed', result['removed'])
else:
    usage()

