"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/

This file creates your application.
"""
import os
import random

import tweepy
from flask import Flask, redirect, render_template, request, url_for
from gillovny.dataset import get_dataset
from werkzeug.contrib.cache import SimpleCache

cache = SimpleCache()
app = Flask(__name__)

app.config['SECRET_KEY'] = str(os.environ.get('SECRET_KEY'))
app.config['CONSUMER_KEY'] = str(os.environ.get('CONSUMER_KEY'))
app.config['CONSUMER_SECRET'] = str(os.environ.get('CONSUMER_SECRET'))

###
# Routing for your application.
###
# @app.route('/api/give_me_love')
# def api():

@app.route('/')
def home():
    """Render website's home page."""
    with app.app_context():
        tweets = get_dataset()
    # Select random tweet
    tweet = random.choice(tweets)
    # id = str(1062383537997971456)
    # tweet = api.get_status(id, tweet_mode = 'extended')
    #
    text = tweet['full_text']
    # text = tweet.extended_tweet['full_text']
    images = []
    videos = []
    # try:
    #     if 'media' in tweet.extended_entities:
    #         for media in tweet.extended_entities['media']:
    #             if 'photo' in media['type']:
    #                 images.append(media['media_url'])
    #             elif 'animated_gif' in media['type']:
    #                 video = media['video_info']['variants'][0]['url']
    #                 print(video)
    #                 #['variants']['url']
    #                 videos.append(video)
    # except AttributeError:
    #     if 'media' in tweet.entities:
    #         for media in tweet.entities['media']:
    #             images.append(media['media_url'])

    urls = []
    instagram = []
    youtube = []

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
    print(urls)
    print(instagram)
    print(youtube)
    print(images)
    return render_template('home.html', text=text, images=images, videos=videos, urls=urls, instagram=instagram, youtube=youtube, raw=tweet)


# @app.route('/about/')
# def about():
#     """Render the website's about page."""
#     return render_template('about.html')
#

###
# The functions below should be applicable to all Flask apps.
###

# @app.route('/<file_name>.txt')
# def send_text_file(file_name):
#     """Send your static text file."""
#     file_dot_text = file_name + '.txt'
#     return app.send_static_file(file_dot_text)
#

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
