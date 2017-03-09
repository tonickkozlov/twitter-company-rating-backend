from flask import Flask, jsonify
from functools import partial
from lib import db
import redis

r = redis.StrictRedis(host='redis', decode_responses=True)

app = Flask(__name__)

def get_tweets_for_account(getter_fn, account, limit=10):
    tweet_scores = getter_fn(account, limit)
    return jsonify({ 'ids': [tweet_id for tweet_id, tweet_score in tweet_scores] })

@app.errorhandler(KeyError)
def unhandled_exception(e):
    app.logger.error(e)
    return jsonify({ 'error': str(e)}), 404

@app.route("/companies")
def get_companies_details():
    ''' will get full list of companies, with details '''
    accounts = db.get_companies(r)
    companies_details = []

    for account in accounts:
        company_details = db.get_company_details(r, account)
        company_details['score'] = db.get_company_score(r, account)
        companies_details.append(company_details)

    return jsonify({ 'companies': companies_details })

@app.route("/company/<account>/best")
def get_best_tweets(account):
    return get_tweets_for_account(partial(db.get_worst_tweets, r), account)

@app.route("/company/<account>/worst")
def get_worst_tweets(account):
    return get_tweets_for_account(partial(db.get_best_tweets, r), account) 
