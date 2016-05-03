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
        StreamListener.__init__(self)
        engine = db_connect(db_config_string)
        create_tables(engine)
        self.Session = sessionmaker(bind=engine, expire_on_commit=False)

    def on_data(self, data):
        data = json.loads(data)
        tweet_id = self.write_tweet(data)
        if tweet_id is not None:
            for hashtag in [x['text'] for x in data['entities']['hashtags']]:
                self.write_hashtags(tweet_id, hashtag)
        return True

    def on_error(self, status):
        print(status)

    def write_tweet(self, data):
        """
        Takes dictionary and writes it to the database
        :param tweet: dictionary containing at least the following fields
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
            session = self.Session()
            try:
                session.add(tweet)
                session.commit()
            except:
                session.rollback()
                raise
            return tweet.id
        return None

    def write_hashtags(self, tweet_id, hashtag):
        """
        Writes the hashtags to it's database
        :param tweet_id - The database id of the tweet
        :param hashtag - contains content of the json document
        :return:
        """
        session = self.Session()
        hashtag = HashTag(tweet_id=tweet_id, hashtag=hashtag)
        try:
            session.add(hashtag)
            session.commit()
        except:
            session.rollback()
            raise
        return None


def run(search_list, config_file):
    """

    :param search_list: python iterable or string (will be converted to list) containing terms to grab
    :param config_file: address of the config file
    :return:
    """

    if isinstance(search_list, str):
        search_list = list(search_list)

    config = ConfigParser.ConfigParser()
    config.read(config_file)

    # Create the database
    tweet_listener = StdOutListener(config.get('setup', 'sqlalchemy_conn'))

    # Set up the listener
    auth = OAuthHandler(config.get('twitter', 'consumer_key'), config.get('twitter', 'consumer_secret'))
    auth.set_access_token(config.get('twitter', 'access_token'), config.get('twitter', 'access_token_secret'))
    stream = Stream(auth, tweet_listener)

    stream.filter(track=search_list)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Database twitter streams.')
    parser.add_argument("-s", "--search_terms", type=str, help="comma separated list of search terms")
    parser.add_argument("-c", "--config_file", type=str, help="config file", default="tweet.ini")
    args = parser.parse_args()

    search_list = args.search_terms.split(",")
    run(search_list, args.config_file)
