''' patch tweet score extractor to return Tweet's score '''

def mock_get_sentiment_score(text, *args, **kwargs):
    return float(text)

from lib import twitter_rating, twitter, db
twitter_rating.get_sentiment_score = mock_get_sentiment_score

from lib.tests.test_helpers import MockTweet, redis_client, foo_company, MockApi
from pytest import approx
from sync_service.sync_tweets import sync_tweets

def test_sync(redis_client, foo_company):
    ' should sync and write all tweets to the db '
    output_tweets = [
        MockTweet(id=0, text='0.25'),
        MockTweet(id=1, text='0.25'),
        MockTweet(id=2, text='0.25'),
    ]
    api = MockApi(*output_tweets)
    for res in sync_tweets(api, redis_client, foo_company):
        pass

    assert db.get_number_of_tweets(redis_client, foo_company) == 3

def test_skip_neutral_tweets(redis_client, foo_company):
    ' should skip neutral tweets '
    output_tweets = [
        MockTweet(id=0, text='0.0'),
        MockTweet(id=1, text='0.0'),
        MockTweet(id=2, text='0.1'),
    ]

    api = MockApi(*output_tweets)
    for res in sync_tweets(api, redis_client, foo_company):
        pass

    assert db.get_number_of_tweets(redis_client, foo_company) == 1
    assert db.get_company_score(redis_client, foo_company) == approx(0.1)

def test_average_score(redis_client, foo_company):
    ' should calculate average score for given tweets '
    output_tweets = [
        MockTweet(id=0, text='0.10'),
        MockTweet(id=1, text='0.20'),
        MockTweet(id=2, text='0.30'),
    ]
    api = MockApi(*output_tweets)
    for res in sync_tweets(api, redis_client, foo_company):
        pass

    expected = (0.10 + 0.20 + 0.30) / 3
    assert db.get_company_score(redis_client, foo_company) ==  approx(expected)

def test_limit_skip_neutral(redis_client, foo_company):
    ' should respect limit while skipping neutral tweets '
    output_tweets = [
        MockTweet(id=0, text='0.1'),
        MockTweet(id=1, text='0.0'), # should be ignored
        MockTweet(id=2, text='0.0'), # should be ignored
        MockTweet(id=3, text='0.2'),
        MockTweet(id=4, text='0.2'), # should be ignored
        MockTweet(id=5, text='0.0'), # should be ignored
    ]

    api = MockApi(*output_tweets)
    for res in sync_tweets(api, redis_client, foo_company, limit=2):
        print('res', res)

    assert db.get_number_of_tweets(redis_client, foo_company) == 2
    assert db.get_company_score(redis_client, foo_company) == approx(0.15)

def test_positive_neagtive(redis_client, foo_company):
    ' should calculate average score for given tweets '
    output_tweets = [
        MockTweet(id=0, text='0.10'),
        MockTweet(id=1, text='-0.10'),
    ]
    api = MockApi(*output_tweets)
    for res in sync_tweets(api, redis_client, foo_company):
        pass

    assert db.get_company_score(redis_client, foo_company) ==  approx(0)

def test_limit_skip_neutral(redis_client, foo_company):
    ' should respect limit while skipping neutral tweets '
    output_tweets = [
        MockTweet(id=0, text='0.1'),
        MockTweet(id=1, text='0.0'), # should be ignored
        MockTweet(id=2, text='0.0'), # should be ignored
        MockTweet(id=3, text='0.2'),
        MockTweet(id=4, text='0.2'), # should be ignored
        MockTweet(id=5, text='0.0'), # should be ignored
    ]

    api = MockApi(*output_tweets)
    for res in sync_tweets(api, redis_client, foo_company, limit=2):
        print('res', res)

    assert db.get_number_of_tweets(redis_client, foo_company) == 2
    assert db.get_company_score(redis_client, foo_company) == approx(0.15)

# def test_limit_0(redis_client, foo_company):
#     api = MockApi()
#     for res in sync_tweets(api, redis_client, foo_company, limit=2):
#         print('res', res)

#     assert db.get_number_of_tweets(redis_client, foo_company) == 2
#     assert db.get_company_score(redis_client, foo_company) == approx(0.15)

def test_prior_tweets(redis_client, foo_company):
    ' should update score correctly if some tweets existed prior to syncing '
    db.write_tweet(redis_client, foo_company, MockTweet(id=100), 0.1)
    db.write_tweet(redis_client, foo_company, MockTweet(id=101), 0.2)
    db.set_company_score(redis_client, foo_company, 0.15)

    assert db.get_number_of_tweets(redis_client, foo_company) == 2

    api = MockApi(
            MockTweet(id=102, text='0.3'),
            MockTweet(id=103, text='0.4')
        )

    for res in sync_tweets(api, redis_client, foo_company):
        pass

    assert db.get_number_of_tweets(redis_client, foo_company) == 4
    expected_score = (0.1 + 0.2 + 0.3 + 0.4) / 4
    assert db.get_company_score(redis_client, foo_company) == approx(expected_score)
def test_max_tweets(redis_client, foo_company):
    ' should remove tweets if `max_tweets` was reached '
    db.write_tweet(redis_client, foo_company, MockTweet(id=100), 0.1)
    db.write_tweet(redis_client, foo_company, MockTweet(id=101), 0.2)
    db.set_company_score(redis_client, foo_company, 0.15)

    api = MockApi(
            MockTweet(id=102, text='0.3'),
            MockTweet(id=103, text='0.4')
        )

    for res in sync_tweets(api, redis_client, foo_company, max_tweets=3):
        pass

    assert db.get_number_of_tweets(redis_client, foo_company) == 3
    expected_score = (0.2 + 0.3 + 0.4) / 3
    assert db.get_company_score(redis_client, foo_company) == approx(expected_score)
    assert db.get_tweets_timeline(redis_client, foo_company, withscores=False) == [b'101', b'102', b'103']

def test_sliding_company_score(redis_client, foo_company):
    ' should update average on every tweet received '
    db.write_tweet(redis_client, foo_company, MockTweet(id=100), 0.1)
    db.write_tweet(redis_client, foo_company, MockTweet(id=101), 0.2)
    db.set_company_score(redis_client, foo_company, 0.15)

    api = MockApi(
            MockTweet(id=102, text='0.3'),
            MockTweet(id=103, text='-0.4'),
            MockTweet(id=104, text='0.4'),
            MockTweet(id=105, text='-0.5')
        )

    tweets_processed = 0
    for res in sync_tweets(api, redis_client, foo_company, max_tweets=4):
        if tweets_processed == 0:
            # [100, 101, 102]
            assert db.get_tweets_timeline(redis_client, foo_company, withscores=False) == [b'100', b'101', b'102']
            expected_score = (0.1 + 0.2 + 0.3) / 3
            assert db.get_company_score(redis_client, foo_company) == approx(expected_score)
        elif tweets_processed == 1:
            assert db.get_tweets_timeline(redis_client, foo_company, withscores=False) == [b'100', b'101', b'102', b'103']
            expected_score = (0.1 + 0.2 + 0.3 - 0.4) / 4
            assert db.get_company_score(redis_client, foo_company) == approx(expected_score)
        elif tweets_processed == 2:
            assert db.get_tweets_timeline(redis_client, foo_company, withscores=False) == [b'101', b'102', b'103', b'104']
            expected_score = (0.2 + 0.3 - 0.4 + 0.4) / 4
            assert db.get_company_score(redis_client, foo_company) == approx(expected_score)
        tweets_processed += 1

    assert db.get_tweets_timeline(redis_client, foo_company, withscores=False) == [b'102', b'103', b'104', b'105']
    expected_score = (0.3 + 0.4 - 0.4 - 0.5) / 4
    assert db.get_company_score(redis_client, foo_company) == approx(expected_score)


