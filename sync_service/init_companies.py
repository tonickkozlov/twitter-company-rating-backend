''' This script gets a list of companies from either stdin or as a parameter, and will go through 
    the list while searching for company accounts on Twitter and writing them into the db '''

import fileinput
import redis

from lib.api import api
from lib import twitter
from lib import db

def add_company(db_instance, company_name):
    ' will find company details by `company_name` and write to db '
    company = twitter.get_company_account(api, company_name)
    db.write_company(db_instance, company)
    print('{0} => {1}'.format(company_name, company.name))
