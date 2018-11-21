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
from tweepy import OAuthHandler

app = Flask(__name__)

app.config['SECRET_KEY'] = str(os.environ.get('SECRET_KEY'))
app.config['CONSUMER_KEY'] = str(os.environ.get('CONSUMER_KEY'))
app.config['CONSUMER_SECRET'] = str(os.environ.get('CONSUMER_SECRET'))

auth = OAuthHandler(app.config['CONSUMER_KEY'], app.config['CONSUMER_SECRET'])
api = tweepy.API(auth)

###
# Routing for your application.
###

@app.route('/')
def home():
    """Render website's home page."""
    query = 'gillovny -filter:retweets'

    MAX_TWEETS = 100

    tweets = []

    for tweet in tweepy.Cursor(api.search,
                               q=query,
                               count=100,
                               include_entities=True,
                               lang='en',
                               result_type='recent').items():

        # Ignore retweets
        if (not tweet.retweeted) and ('RT @' not in tweet.text) and (tweet.text[0] != '@'):
            tweets.append(tweet)

        if len(tweets) > MAX_TWEETS:
            break

    # Select random tweet
    tweet = random.choice(tweets)

    text = tweet.text
    images = []

    if 'media' in tweet.entities:
        for image in tweet.entities['media']:
            images.append(image['media_url'])

    print(images)
    return render_template('home.html', text=text, images=images)


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
