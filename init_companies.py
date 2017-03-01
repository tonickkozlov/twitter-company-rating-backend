''' This script gets a list of companies from either stdin or as a parameter, 
    and searches twitter users trying to find the official account. The scrtipt is 
    semi-automatic - it will show the user a list of all available matches for companies and will
    ask to pick one'''

from api import api
from twitter_getter import get_cursored_data
from nltk.metrics.distance import edit_distance

import fileinput

def get_company_account(company_name):
    cursor = get_cursored_data(api.search_users, q=company_name, limit=10)
    candidates = [company for company in cursor]

    # try to find the perfect match - if lowercase company name matches screen name
    match = [candidate for candidate in candidates if
            candidate.screen_name.lower() == company_name.replace(' ', '').lower()]

    if len(match) > 0:
        company = match[0]
        print('Found a perfect match for company {0}: @{1}'
                .format(company_name, company.screen_name))
        return company

    # if finding a perfect match failed - ask user for best choice,
    # provide assistance with edit distance
    edit_distances = [edit_distance(company_name, candidate.name) for candidate in candidates]
    default_answer = edit_distances.index(min(edit_distances))

    print('Select company for {0} from the list below [{1}]'.format(company_name, default_answer))
    for (i, company) in enumerate(candidates):
        print(i, '\t|', company.screen_name, '\t|', company.name, '\t|', 'verified' if company.verified else '')

    answer = input()
    if answer == '':
        return candidates[default_answer]

    if answer == '-':
        return None

    if answer[0] == '@':
        return get_company_account(answer)

    return candidates[int(answer)]


if __name__ == '__main__':
    print (get_company_account('@amazon'))
    # companies = {}
    # for line in fileinput.input():
    #     company_name = line.strip()
    #     companies[company_name] = get_company_account(company_name)
