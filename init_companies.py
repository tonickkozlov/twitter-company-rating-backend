''' This script gets a list of companies from either stdin or as a parameter, and will go through 
    the list while searching for company accounts on Twitter and writing them into the db '''

import fileinput

import redis
from api import api

import twitter
import db

def add_company(db_instance, company_name):
    ' will find company details by `company_name` and write to db '
    company = twitter.get_company_account(api, company_name)
    db.write_company(db_instance, company)
    print('got company {0}'.format(company_name))


r = redis.StrictRedis(decode_responses=True)
if __name__ == '__main__':
    r = redis.StrictRedis(decode_responses=True)
    for line in fileinput.input():
        company_name = line.strip()
        add_company(r, company_name)
