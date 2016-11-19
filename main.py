import tweepy

consumer_key = 'TsC0lTgq5GXHoxfhsy4NbOAYv'
consumer_secret = 'rEwCMXv2kt3AkbPS28zAnVZbhmBhMBgOLhExPcAMZX0K7VP49s'

access_token = '729020700925665280-kK7haumye62uYWaiC6qK51cl11f0NgA'
access_token_secret = '4vgn7lcBj6rSHA0nIThDxizg8FXZudoy4JBuTkAmARBwG'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

public_tweets = api.home_timeline()
for tweet in public_tweets:
    print(tweet.text)
