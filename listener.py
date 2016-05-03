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
        tweet_id = self.write_tweet(**data)
        if tweet_id is not None:
            # Add hashtag
            self.write_hashtags(tweet_id, data['entities']['hashtags'])

        return True

    def on_error(self, status):
        print(status)

    @staticmethod
    def write_tweet(data):
        """
        Takes dictionary and writes it to the database
        :param tweet: dictionary containing the following fields
            'text' - the content of the tweet
            'user'['name'] = twitter real name
            'user'['screen_name'] = twitter screen name
            'user'['id_str'] = twitter id string
            'user'['verified] = Is this user verified (blue checkmark)
            'timestamp' = time stamp (unix time)
            'user'['friends_count'] = How many people this user follows
            'user'['followers_count'] = How many people follow this user
        :return: tweet id
        """
        if 'user' in data and 'text' in data:
            tweet = Tweet(tweet=data['text'], name=data['user']['name'], username=data['user']['screen_name'],
                          user_id=data['user']['id_str'], verified=data['user']['verified'],
                          timestamp=data['timestamp_ms'], following=data['user']['friends_count'],
                          followers=data['user']['followers_count'])
            db.session.add(tweet)
            db.session.commit()
            return tweet.id
        return None

    @staticmethod
    def write_hashtags(tweet_id, hashtag):
        """
        :return:
        """
        pass


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
