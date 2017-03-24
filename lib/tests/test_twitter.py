from test_helpers import MockTweet, MockApi
from lib import twitter

def test_get_tweets():
    ' get_tweets_about_company will give tweets from the api one by one '
    output_tweets = [
        MockTweet(id=0, text='foo'),
        MockTweet(id=1, text='bar'),
        MockTweet(id=2, text='baz'),
    ]
    api = MockApi(*output_tweets)

    tweets = [tweet for tweet in twitter.get_tweets_about_company(api, 'foobar')]
    assert len(tweets) == 3
    assert tweets == output_tweets

def test_limit():
    ' will return only tweets limited by `limit` '

    output_tweets = [
        MockTweet(id=0, text='foo'),
        MockTweet(id=1, text='bar'),
        MockTweet(id=2, text='baz'),
    ]
    api = MockApi(*output_tweets)

    tweets = [tweet for tweet in twitter.get_tweets_about_company(api, 'foobar', limit=1)]
    assert len(tweets) == 1
    assert tweets == [output_tweets[0]]

def test_skip_retweets():
    ' should skip re-tweet defined by .retweeted field or starting with RT '

    ' will return only tweets limited by `limit` '

    output_tweets = [
        MockTweet(id=0, text='foo', retweeted=True),
        MockTweet(id=1, text='RT bar'),
        MockTweet(id=2, text='baz'),
    ]
    api = MockApi(*output_tweets)

    tweets = [tweet for tweet in twitter.get_tweets_about_company(api, 'foobar')]

    assert len(tweets) == 1
    assert tweets == [output_tweets[2]]

def test_limit_skip_retweets():
    ' Should apply limiting after skipping re-tweets ' 
    output_tweets = [
        MockTweet(id=0, text='foo', retweeted=True),
        MockTweet(id=1, text='RT bar'),
        MockTweet(id=2, text='baz'),
        MockTweet(id=2, text='bazbaz'),
    ]
    api = MockApi(*output_tweets)

    tweets = [tweet for tweet in twitter.get_tweets_about_company(api, 'foobar', limit=1)]

    assert len(tweets) == 1
    assert tweets == [output_tweets[2]]
