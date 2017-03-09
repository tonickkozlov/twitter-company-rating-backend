import tweepy

_consumer_key = 'TsC0lTgq5GXHoxfhsy4NbOAYv'
_consumer_secret = 'rEwCMXv2kt3AkbPS28zAnVZbhmBhMBgOLhExPcAMZX0K7VP49s'

_access_token = '729020700925665280-kK7haumye62uYWaiC6qK51cl11f0NgA'
_access_token_secret = '4vgn7lcBj6rSHA0nIThDxizg8FXZudoy4JBuTkAmARBwG'

auth = tweepy.OAuthHandler(_consumer_key, _consumer_secret)
auth.set_access_token(_access_token, _access_token_secret)

api = tweepy.API(auth)
