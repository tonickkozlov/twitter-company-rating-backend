''' Gets company twitter account name by its actual name'''

import sys
from api import api
from twitter_getter import get_company_account

company_name = sys.argv[1]

print(company_name,'|', get_company_account(api, company_name))
