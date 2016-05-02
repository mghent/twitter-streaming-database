from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///tutorial.db"
db = SQLAlchemy(app)

class Tweet(db.Model):
    __tablename__ = "tweet"

    id = db.Column(db.Integer, primary_key=True)
    tweet = db.Column(db.String(140))
    name = db.Column(db.String(100))
    username = db.Column(db.String(100))
    user_id = db.Column(db.String(40))
    verified = db.Column(db.Boolean)
    timestamp_ms = db.Column(db.Integer)
    following = db.Column(db.Integer)
    followers = db.Column(db.Integer)

    def __init__(self, tweet, name, username, user_id, verified, timestamp, hashtags, following, followers):
        self.tweet = tweet
        self.name = name
        self.username = username
        self.user_id = user_id
        self.verified = verified
        self.timestamp_ms = timestamp
        self.following = following
        self.followers = followers

        # self.hashtags = ",".join([x['text'] for x in hashtags if x['text'] in hashtags]) if len(hashtags) > 0 else ""


    def __repr__(self):
        return '<User %r>' % self.username

class HashTag(db.Model):
    __tablename__ = "hashtags"
    id = db.Column(db.Integer, primary_key=True)
    tweet_id = db.Column(db.Integer, db.ForeignKey('tweet.id'))
    hashtag = db.Column(db.String(100))


