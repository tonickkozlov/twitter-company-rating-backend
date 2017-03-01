from api import api
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from twitter_getter import get_tweets_by_company
from tweet_utils import *

sid = SentimentIntensityAnalyzer()
c = get_tweets_by_company(api, 'microsoft', limit=10)

for tweet in c:
    norm = get_text_normalized(tweet)
    print("========================================", tweet.id, "========================================")
    print(tweet.text)
    print(norm)
    print(sid.polarity_scores(tweet.text))
    print(sid.polarity_scores(' '.join(norm)))
