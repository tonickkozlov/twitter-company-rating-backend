import redis
from lib import db
import sys

r = redis.StrictRedis(host='redis', decode_responses=True)
for company in db.get_companies(r):
	try:
		print('company', company, 'has', db.get_number_of_tweets(r, company), 'tweets')
		print('removing unneccessary')
		for tweet_id in db.get_tweets_timeline(r, company, withscores=False):
			tweet_score = db.get_tweet_score(r, company, tweet_id)
			if (tweet_score == 0.0):
				print('removing', tweet_id, tweet_score)
				db.remove_tweets(r, company, tweet_id)

		print('company', company, 'has', db.get_number_of_tweets(r, company), 'tweets')
		print('score before', db.get_company_score(r, company))
		db.update_company_overall_score(r, company)
		print('score after', db.get_company_score(r, company))
	except Exception:
		r.delete('companyscore:{0}'.format(company))
		pass

