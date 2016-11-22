# -*- coding: utf-8 -*-
import os.path as op
import sys
import datetime

project_path = '/Users/manumouss/workspace/ratp_traffic' #change for env variable
sys.path.append(op.join(project_path, 'src'))
from utils import get_tweets_for_user, print_stats

from flask import Flask, send_file
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"


@app.route("/print_stats/<twitter_name>")
def print_stat(twitter_name):
    """ compute the figures if needed, then serves it """
    token = datetime.datetime.now().strftime("%Y%m%d")
    events = get_tweets_for_user(target_user='@'+twitter_name, n_rounds=16)
    figure_path = op.join(project_path, 'figures', '%s_%s.png' % (twitter_name, token))
    print "Entering stat method"
    returned_path = print_stats(events, figure_path=figure_path)
    print returned_path
    
    return send_file(figure_path, mimetype='image/png')
    


if __name__ == '__main__':
    app.run('0.0.0.0', 5021)