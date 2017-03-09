FROM        ubuntu:16.04
MAINTAINER  Anton Kozlov tonickkozlov@me.com
RUN         apt-get update && apt-get install -y python3 python3-pip
RUN         pip3 install --upgrade pip redis tweepy nltk
RUN         python3 -m nltk.downloader vader_lexicon

VOLUME ["/opt/server"]
WORKDIR /opt/server
