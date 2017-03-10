from flask import Flask, jsonify
from functools import wraps
from lib import db
import redis

r = redis.StrictRedis(host='redis', decode_responses=True)

app = Flask(__name__)

def jsonify_tweets(tweet_getter):
    ''' decorator that will raise a KeyError if a company does not exist '''
    @wraps(tweet_getter)
    def wrapper(*args, **kwargs):
        result = tweet_getter(*args, **kwargs)
        print('res', result)
        return jsonify({ 'ids': [tweet_id for tweet_id, tweet_score in result] })

    return wrapper

def get_tweets_for_account(getter_fn, *args):
    tweet_scores = getter_fn(*args)
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

@app.route("/company/<account>/length")
def get_number_of_tweets(account):
    return jsonify({ 'length': db.get_number_of_tweets(r, account) })

@app.route("/company/<account>")
@jsonify_tweets
def get_tweets(account):
    return db.get_tweets_timeline(r, account)

@app.route("/company/<account>/best")
@jsonify_tweets
def get_best_tweets(account):
    return db.get_best_tweets(r, account, limit=10)

@app.route("/company/<account>/worst")
@jsonify_tweets
def get_worst_tweets(account):
    return db.get_worst_tweets(r, account, limit=10)
