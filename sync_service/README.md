# Synchronization service

Fetches tweets from Twitter using [tweepy](http://www.tweepy.org) and analyses them using [nltk](http://www.nltk.org).

## Initialization

```bash
echo "Company Name" | python3 -m sync_service init
```

## Synchronization

```bash
python3 -m sync_service sync
```

or, to sync tweets mentioning individual account, run
```bash
python3 -m sync_service sync accountname
```

The tweets are fetched from most recent to lease recent using cursoring.
To learn more about specifics of working with Twitter's API please refer to [Official Twitter API docs](https://dev.twitter.com/).
