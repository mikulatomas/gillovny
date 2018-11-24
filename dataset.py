import tweepy
from gillovny import cache
from tweepy import OAuthHandler


def get_dataset():
    dataset = cache.get('dataset')

    if dataset is None:
        print("CREATING DATASET")
        auth = OAuthHandler(current_app.config['CONSUMER_KEY'], current_app.config['CONSUMER_SECRET'])
        api = tweepy.API(auth)

        query = 'gillovny -filter:retweets'

        MAX_TWEETS = 200

        dataset = []

        for tweet in tweepy.Cursor(api.search,
                                   q=query,
                                   count=100,
                                   include_entities=True,
                                   lang='en',
                                   tweet_mode='extended',
                                   result_type='recent').items():

            # Ignore retweets
            if (not tweet.retweeted) and ('RT @' not in tweet.full_text) and (tweet.full_text[0] != '@'):
                if not tweet.is_quote_status:
                    dataset.append(tweet._json)

            if len(dataset) > MAX_TWEETS:
                break

        cache.set('dataset', dataset, timeout=60 * 5)

    return dataset
