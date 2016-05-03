import json
import argparse

import ConfigParser

from sqlalchemy.orm import sessionmaker

from models import Tweet, HashTag, db_connect, create_tables

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream


class StdOutListener(StreamListener):
    """ A listener handles tweets that are received from the stream.
    This is a basic listener that just prints received tweets to stdout.
    """

    def __init__(self, db_config_string):
        engine = db_connect(db_config_string)
        create_tables(engine)
        self.Session = sessionmaker(bind=engine)

    def on_data(self, data):
        data = json.loads(data)
        tweet_id = self.write_tweet(**data)
        if tweet_id is not None:
            self.write_hashtags(tweet_id, data['entities']['hashtags'])

        return True

    def on_error(self, status):
        print(status)

    def write_tweet(self, data):
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
        session = self.Session()
        if 'user' in data and 'text' in data:
            tweet = Tweet(tweet=data['text'], name=data['user']['name'], username=data['user']['screen_name'],
                          user_id=data['user']['id_str'], verified=data['user']['verified'],
                          timestamp=data['timestamp_ms'], following=data['user']['friends_count'],
                          followers=data['user']['followers_count'])
            try:
                session.add(tweet)
                session.commit()
            except:
                session.rollback()
                raise
            finally:
                session.close()
            return tweet.id
        return None

    @staticmethod
    def write_hashtags(tweet_id, hashtag):
        """
        :return:
        """

        # self.hashtags = ",".join([x['text'] for x in hashtags if x['text'] in hashtags]) if len(hashtags) > 0 else ""

        pass


def run(search_list, config_file):
    config = ConfigParser()
    config.read(config_file)

    # Create the database
    tweet_listener = StdOutListener(config.get('setup', 'sqlalchemy_conn'))

    # Set up the listener
    auth = OAuthHandler(config.get('twitter', 'consumer_key'), config.get('twitter', 'consumer_secret'))
    auth.set_access_token(config.get('twitter', 'access_token'), config.get('twitter', 'access_token_secret'))
    stream = Stream(auth, tweet_listener)
    stream.filter(track=[search_list])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Database twitter streams.')
    parser.add_argument('search_terms', type=str, nargs='+', help='comma separated list of search terms')
    parser.add_argument('config_file', type=str, nargs='+', help='config file', default="tweet.ini")
    args = parser.parse_args()

    search_list = args.search_terms.split(",")
    run(search_list, args.config_file)
