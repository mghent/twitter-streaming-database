import json
import argparse

import ConfigParser

from models import db, Tweet, HashTag

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream


class StdOutListener(StreamListener):
    """ A listener handles tweets that are received from the stream.
    This is a basic listener that just prints received tweets to stdout.
    """

    def on_data(self, data):
        data = json.loads(data)
        if 'user' in data and 'text' in data:
            tweet = Tweet(data['text'], data['user']['name'], data['user']['screen_name'],
                          data['user']['id_str'], data['user']['verified'], data['timestamp_ms'],
                          data['entities']['hashtags'], data['user']['friends_count'], data['user']['followers_count'])
        db.session.add(tweet)
        db.session.commit()
        return True

    def on_error(self, status):
        print(status)


def run(search_list):
    tweet_listener = StdOutListener()
    config = ConfigParser()
    config.read("tweet.ini")

    auth = OAuthHandler(config.get('twitter', 'consumer_key'), config.get('twitter', 'consumer_secret'))
    auth.set_access_token(config.get('twitter', 'access_token'), config.get('twitter', 'access_token_secret'))
    stream = Stream(auth, tweet_listener)
    stream.filter(track=[search_list])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Database twitter streams.')
    parser.add_argument('search_terms', type=str, nargs='+', help='comma separated list of search terms')
    args = parser.parse_args()
    search_list = args.search_terms.split(",")
    run(search_list)
