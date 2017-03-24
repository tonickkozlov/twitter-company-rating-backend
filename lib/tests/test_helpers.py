import pytest
from lib import db, twitter
from mockredis import mock_strict_redis_client as MockRedis

class MockApi:

    def mock_get_cursored_data(endpoint, *args, **kwargs):
        return endpoint()

    ' patch twitters get_cursored_data to bypass calls to actual Twitter impl '
    twitter.get_cursored_data = mock_get_cursored_data

    ' Simulates twitters api class '
    def __init__(self, *tweet_list):
        self.tweet_list = tweet_list

    def search(self, *args, **kwargs):
        ' will give tweets from tweet_list '
        return (tweet for tweet in self.tweet_list)

class MockCompany:
    def __init__(self, name, account, profile_image_url):
        self.name = name
        self.screen_name = account
        self.profile_image_url = profile_image_url

class MockTweet:
    def __init__(self, id, text='', retweeted=False, entities=None):
        self.id = id
        self.text = text
        self.retweeted = retweeted
        self.entities = entities

@pytest.fixture
def redis_client():
    return MockRedis()

@pytest.fixture
def foo_company(redis_client):
    account = 'foo'
    company = MockCompany(account=account, name='bar', profile_image_url='baz')
    db.write_company(redis_client, company)
    return account

