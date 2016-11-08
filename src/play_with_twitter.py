# -*- coding: utf-8 -*-
"""
Created on Wed Oct 12 16:28:29 2016

@author: manu
"""


from utils import get_tweets_for_user

import os.path as op
outputfile = op.join('C:/Users/Manu/workspace/ratp_traffic/src',
                     'saved_tweets.json')

events = get_tweets_for_user(target_user='@RER_A', n_rounds=10)
#events.save(outputfile)

durations_by_causes = events.get_statistics()
from pandas import DataFrame

