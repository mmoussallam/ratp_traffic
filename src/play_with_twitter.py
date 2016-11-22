# -*- coding: utf-8 -*-
"""
Created on Wed Oct 12 16:28:29 2016

@author: manu
"""
import utils
from utils import get_tweets_for_user, print_stats
import os.path as op
from pandas import DataFrame
import matplotlib.pyplot as plt


here = op.abspath(op.dirname(utils.__file__))
outputfile = op.join(here,'..','data',
                     'saved_tweets.json')


events = get_tweets_for_user(target_user='@RERB', n_rounds=16)
events.save(outputfile)

path = print_stats(events)
#loaded_events = load_from_json(outputfile)

# explore durations by causes
#durations_by_causes = events.get_durations_by_cause()
#df_causes = DataFrame( [{"cause":k, "duration":t.seconds / 3600.} for k,v in durations_by_causes.iteritems() for t in v])
#
## explore durations by time
#durations_by_times = events.get_durations_by_time()
#df_times = DataFrame([{"time":k, "duration":t.seconds / 3600.} for k,v in durations_by_times.iteritems() for t in v])
#
#fig = plt.figure(figsize=(8,12))
#ax = plt.subplot(211)
#df_causes.boxplot(column='duration', by='cause', rot=75, ax=ax)
#ax = plt.subplot(212)
#df_times.boxplot(column='duration', by='time', ax=ax)
#fig.tight_layout()
