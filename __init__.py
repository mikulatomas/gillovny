"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/

This file creates your application.
"""

import os
import random

import tweepy
from flask import Flask, jsonify, redirect, render_template, request, url_for
from flask_caching import Cache
from tweepy import OAuthHandler

app = Flask(__name__)
cache = Cache()

cache_servers = os.environ.get('MEMCACHIER_SERVERS')
if cache_servers == None:
    # Fall back to simple in memory cache (development)
    cache.init_app(app, config={'CACHE_TYPE': 'simple'})
else:
    cache_user = os.environ.get('MEMCACHIER_USERNAME') or ''
    cache_pass = os.environ.get('MEMCACHIER_PASSWORD') or ''
    cache.init_app(app,
        config={'CACHE_TYPE': 'saslmemcached',
                'CACHE_MEMCACHED_SERVERS': cache_servers.split(','),
                'CACHE_MEMCACHED_USERNAME': cache_user,
                'CACHE_MEMCACHED_PASSWORD': cache_pass,
                'CACHE_OPTIONS': { 'behaviors': {
                    # Faster IO
                    'tcp_nodelay': True,
                    # Keep connection alive
                    'tcp_keepalive': True,
                    # Timeout for set/get requests
                    'connect_timeout': 2000, # ms
                    'send_timeout': 750 * 1000, # us
                    'receive_timeout': 750 * 1000, # us
                    '_poll_timeout': 2000, # ms
                    # Better failover
                    'ketama': True,
                    'remove_failed': 1,
                    'retry_timeout': 2,
                    'dead_timeout': 30}}})

app.config['SECRET_KEY'] = str(os.environ.get('SECRET_KEY'))
app.config['CONSUMER_KEY'] = str(os.environ.get('CONSUMER_KEY'))
app.config['CONSUMER_SECRET'] = str(os.environ.get('CONSUMER_SECRET'))

###
# Routing for your application.
###
def get_id(id):
    auth = OAuthHandler(app.config['CONSUMER_KEY'], app.config['CONSUMER_SECRET'])
    api = tweepy.API(auth)

    tweet = api.get_status(id, tweet_mode='extended')
    text = tweet.full_text

    images = []
    videos = []

    try:
        if 'media' in tweet.extended_entities:
            for media in tweet.extended_entities['media']:
                if 'photo' in media['type']:
                    images.append(media['media_url'])
                elif ('animated_gif' in media['type']) or ('video' in media['type']):
                    video = media['video_info']['variants'][0]['url']
                    videos.append(video)
    except AttributeError:
        if 'media' in tweet.entities:
            for media in tweet.entities['media']:
                images.append(media['media_url'])

    urls = []
    instagram = []
    youtube = []

    from urllib.parse import urlparse, parse_qs

    if 'urls' in tweet.entities:
        for url in tweet.entities['urls']:
            url = url['expanded_url']

            parsed = urlparse(url)

            if 'youtube' in parsed.netloc:
                query = parse_qs(parsed.query)
                video_id = query['v'][0]
                youtube.append(video_id)
            elif 'instagram' in parsed.netloc:
                instagram_id = parsed.path.split('/')[2]
                instagram.append(instagram_id)
            else:
                urls.append(url)

    return jsonify(text=text,
                   images=images,
                   videos=videos,
                   urls=urls,
                   instagram=instagram,
                   youtube=youtube)


@app.route('/api/images')
def api_images():
    return get_id('1064146450010071040')

@app.route('/api/youtube')
def api_youtube():
    return get_id('1062383537997971456')

@app.route('/api/video')
def api_video():
    return get_id('1064577977898463234')

@app.route('/api/instagram')
def api_instagram():
    return get_id('1064658936119218176')

@app.route('/api/url')
def api_url():
    return get_id('1065044175211687936')



@app.route('/api/')
def api():
    tweets = get_dataset()
    tweet = random.choice(tweets)
    text = tweet.full_text

    images = []
    videos = []

    try:
        if 'media' in tweet.extended_entities:
            for media in tweet.extended_entities['media']:
                if 'photo' in media['type']:
                    images.append(media['media_url'])
                elif ('animated_gif' in media['type']) or ('video' in media['type']):
                    video = media['video_info']['variants'][0]['url']
                    videos.append(video)
    except AttributeError:
        if 'media' in tweet.entities:
            for media in tweet.entities['media']:
                images.append(media['media_url'])

    urls = []
    instagram = []
    youtube = []

    from urllib.parse import urlparse, parse_qs

    if 'urls' in tweet.entities:
        for url in tweet.entities['urls']:
            url = url['expanded_url']

            parsed = urlparse(url)

            if 'youtube' in parsed.netloc:
                query = parse_qs(parsed.query)
                video_id = query['v'][0]
            elif 'youtu' in parsed.netloc:
                video_id = parsed.path.split('/')[1]
                youtube.append(video_id)
            elif 'instagram' in parsed.netloc:
                instagram_id = parsed.path.split('/')[2]
                instagram.append(instagram_id)
            else:
                urls.append(url)

    user = tweet.user.name
    retweet = tweet.retweet_count
    favorite = tweet.favorite_count

    return jsonify(text=text,
                   images=images,
                   videos=videos,
                   urls=urls,
                   instagram=instagram,
                   youtube=youtube,
                   user=user,
                   retweet=retweet,
                   favorite=favorite)




@cache.cached(timeout=50, key_prefix='all_comments')
def get_dataset():
    auth = OAuthHandler(app.config['CONSUMER_KEY'], app.config['CONSUMER_SECRET'])
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
                dataset.append(tweet)

        if len(dataset) > MAX_TWEETS:
            break

    return dataset

@app.route('/')
def home():
    # tweets = get_dataset()
    # # Select random tweet
    # tweet = random.choice(tweets)
    # text = tweet.full_text
    # # text = tweet.extended_tweet['full_text']
    # images = []
    # videos = []
    #
    # try:
    #     if 'media' in tweet.extended_entities:
    #         for media in tweet.extended_entities['media']:
    #             if 'photo' in media['type']:
    #                 images.append(media['media_url'])
    #             elif 'animated_gif' in media['type']:
    #                 video = media['video_info']['variants'][0]['url']
    #                 videos.append(video)
    # except AttributeError:
    #     if 'media' in tweet.entities:
    #         for media in tweet.entities['media']:
    #             images.append(media['media_url'])
    #
    # urls = []
    # instagram = []
    # youtube = []
    #
    # from urllib.parse import urlparse, parse_qs
    #
    # if 'urls' in tweet.entities:
    #     for url in tweet.entities['urls']:
    #         url = url['expanded_url']
    #
    #         parsed = urlparse(url)
    #
    #         if 'youtube' in parsed.netloc:
    #             query = parse_qs(parsed.query)
    #             video_id = query['v'][0]
    #             youtube.append(video_id)
    #         elif 'instagram' in parsed.netloc:
    #             instagram_id = parsed.path.split('/')[2]
    #             instagram.append(instagram_id)
    #         else:
    #             urls.append(url)
    #
    # return render_template('home.html', text=text, images=images, videos=videos, urls=urls, instagram=instagram, youtube=youtube, raw=tweet)
    return render_template('home.html')


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=600'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)
