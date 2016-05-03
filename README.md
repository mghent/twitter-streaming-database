# twitter-streaming-database
Uses tweepy and SQLAlchemy to parse the twitter streaming api for supplied keywords and databases the results.

# Setup

1. Setup a twitter app at https://apps.twitter.com/
2. Create a config file with the same fields as template.ini. Add the consumer_key, consumer_secret, access_token and access_token_secret
3. Add a sql alchemy database connection string to the [setup] section in this ini file
4. Run the app with `python listener.py --search_terms=term1,term2 --config_file=<config.ini>
