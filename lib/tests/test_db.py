import pytest
from test_helpers import redis_client, foo_company, MockTweet, MockCompany
import lib.db as db

def test_add_company(redis_client, foo_company):
    ' Adding a company adds it a the list of companies '
    company = MockCompany(account='foo', name='bar', profile_image_url='baz')
    db.write_company(redis_client, company)
    companies = db.get_companies(redis_client)
    assert b'foo' in companies

def test_double_add_company(redis_client):
    ' Should only add a company once '
    company = MockCompany(account='foo', name='bar', profile_image_url='baz')
    db.write_company(redis_client, company)
    db.write_company(redis_client, company)
    companies = db.get_companies(redis_client)
    assert len(companies) == 1

def test_empty_company(redis_client):
    ' Should throw KeyError if the company does not exist'
    with pytest.raises(KeyError):
        db.get_company_details(redis_client, 'company_does_not_exist')

def test_get_company(redis_client):
    ' Should fetch details for given company '
    company = MockCompany(account='foo', name='bar', profile_image_url='baz')
    db.write_company(redis_client, company)
    details = db.get_company_details(redis_client, 'foo')
    assert details['account'] == b'foo'
    assert details['name'] == b'bar'
    assert details['profile_image_url'] == b'baz'

def test_write_tweet(redis_client, foo_company):
    tweet = MockTweet(id=100)
    db.write_tweet(redis_client, foo_company, tweet, tweet_score=0.8)
    timeline = db.get_tweets_timeline(redis_client, foo_company)
    assert db.get_tweet_score(redis_client, foo_company, b'100') == 0.8
    assert db.get_number_of_tweets(redis_client, foo_company) == 1
    assert len(timeline) == 1
    assert timeline[0][0] == b'100' # tweet id is used as a key
    assert timeline[0][1] == 100    # and also used as score

def test_rem_tweet(redis_client, foo_company):
    tweet1 = MockTweet(id=100)
    tweet2 = MockTweet(id=101)
    db.write_tweet(redis_client, foo_company, tweet1, tweet_score=0.8)
    db.write_tweet(redis_client, foo_company, tweet2, tweet_score=0.8)
    assert db.get_number_of_tweets(redis_client, foo_company) == 2
    assert len(db.get_tweets_timeline(redis_client, foo_company)) == 2
    db.remove_tweets(redis_client, foo_company, 100, 101)
    assert db.get_number_of_tweets(redis_client, foo_company) == 0
    assert len(db.get_tweets_timeline(redis_client, foo_company)) == 0

def test_get_positive_tweets(redis_client, foo_company):
    ' Writing a tweet with a positive score results in best_tweets being populated ' 
    tweet = MockTweet(id=100)
    db.write_tweet(redis_client, foo_company, tweet, tweet_score=0.8)
    best_tweets = db.get_best_tweets(redis_client, foo_company)
    assert len(best_tweets) == 1
    worst_tweets = db.get_worst_tweets(redis_client, foo_company)
    assert len(worst_tweets) == 0

def test_write_positive_tweet(redis_client, foo_company):
    ' Writing a tweet with a positive score results in worst_tweets being populated ' 
    tweet = MockTweet(id=100)
    db.write_tweet(redis_client, foo_company, tweet, tweet_score=-0.8)
    best_tweets = db.get_best_tweets(redis_client, foo_company)
    assert len(best_tweets) == 0
    worst_tweets = db.get_worst_tweets(redis_client, foo_company)
    assert len(worst_tweets) == 1

def test_remove_tweet(redis_client, foo_company):
    ' Calling db.remove_tweets will correctly remove a tweet '
    tweet = MockTweet(id=100)
    db.write_tweet(redis_client, foo_company, tweet, tweet_score=-0.8)
    db.remove_tweets(redis_client, foo_company, 100)

    assert len(db.get_best_tweets(redis_client, foo_company)) == 0
    assert len(db.get_tweets_timeline(redis_client, foo_company)) == 0

def test_empty_company_score(redis_client, foo_company):
    ' Should return 0 for companies with no score set '
    assert db.get_company_score(redis_client, foo_company) == 0

def test_company_score(redis_client, foo_company):
    ' Should be able to get/set company score '
    db.set_company_score(redis_client, foo_company, 0.25)
    assert db.get_company_score(redis_client, foo_company) == 0.25

def test_get_max_tweet_id(redis_client, foo_company):
    ' Should return max tweet id from all the tweets for the company '
    assert db.get_max_tweet_id(redis_client, foo_company) == 0 

def test_get_max_tweet_id(redis_client, foo_company):
    db.write_tweet(redis_client, foo_company, MockTweet(id=100), 0.2)
    assert db.get_max_tweet_id(redis_client, foo_company) == 100 
    db.write_tweet(redis_client, foo_company, MockTweet(id=110), 0.2)
    assert db.get_max_tweet_id(redis_client, foo_company) == 110 
    ' Should return max tweet id from all the tweets for the company '
