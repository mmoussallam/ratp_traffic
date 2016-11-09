# -*- coding: utf-8 -*-
"""
Created on Wed Oct 12 16:28:29 2016

@author: manu
"""

from utils import get_tweets_for_user
import os.path as op
from pandas import DataFrame
import matplotlib.pyplot as plt
import numpy as np

outputfile = op.join('C:/Users/Manu/workspace/ratp_traffic/src',
                     'saved_tweets.json')

events = get_tweets_for_user(target_user='@RER_A', n_rounds=10)
#events.save(outputfile)

# explore durations by causes
durations_by_causes = events.get_statistics()

datas = [{"cause":k, "duration":t.seconds / 60} for k,v in durations_by_causes.iteritems() for t in v]

df = DataFrame(datas)
df.groupby('cause').describe()

longs = [e for e in events.eventlist if (e.get_duration().seconds / 60) > 800]