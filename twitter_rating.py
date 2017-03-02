from api import api
from re import finditer
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from tweet_utils import *

def camel_case_split(identifier):
    ' will space-separate camel case words '
    matches = finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', identifier)
    return ' '.join([m.group(0) for m in matches])

def get_sentiment_score(text, entities):
    # hash tags and camelCase words do not contribute to overall tweet score.
    # So try to extract data from entities and dump it in the end od tweet's text to 
    # get them analyzed by Vader
    hashtags = ' '.join([camel_case_split(hashtag['text']) for hashtag in entities['hashtags']])

    sid = SentimentIntensityAnalyzer()
    return sid.polarity_scores(text + ' ' + hashtags)['compound']

if __name__ == '__main__':
    import redis
    import json
    import sys
    print (sys.argv[1])
    r = redis.StrictRedis(decode_responses=True)
    [text, entities] = r.hmget('tweet:{0}'.format(sys.argv[1]), 'text', 'entities')
    entities = json.loads(entities)
    print (get_sentiment_score(text, entities))


