from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

def db_connect(db_string):
    """
    Returns sqlalchemy engine instance
    """
    return create_engine(db_string)


def create_tables(engine):
    """
    Creates tables (DeclarativeBase subclassed)
    :param engine - SQLAlchemy database engine
    """
    Base.metadata.create_all(engine)


class Tweet(Base):
    __tablename__ = "tweet"

    id = Column(Integer, primary_key=True)
    tweet = Column(String(140))
    name = Column(String(100))
    username = Column(String(100))
    user_id = Column(String(40))
    verified = Column(Boolean)
    timestamp_ms = Column(Integer)
    following = Column(Integer)
    followers = Column(Integer)

    def __init__(self, tweet, name, username, user_id, verified, timestamp, following, followers):
        self.tweet = tweet
        self.name = name
        self.username = username
        self.user_id = user_id
        self.verified = verified
        self.timestamp_ms = timestamp
        self.following = following
        self.followers = followers

    def __repr__(self):
        return '<User %r>' % self.username

class HashTag(Base):
    __tablename__ = "hashtags"
    id = Column(Integer, primary_key=True)
    tweet_id = Column(Integer, ForeignKey('tweet.id'))
    hashtag = Column(String(100))

    def __init__(self, tweet_id, hashtag):
        self.tweet_id = tweet_id
        self.hashtag = hashtag

