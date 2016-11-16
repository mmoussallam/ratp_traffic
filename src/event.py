# -*- coding: utf-8 -*-
"""
Created on Mon Nov 07 23:27:32 2016

@author: Manu
"""
import json
from datetime import datetime
from constants import causes, ESTIMATION
import re

def _parse_date(tweet):
    return datetime.strptime(tweet['created_at'].replace('+0000 ','')
                                       , "%a %b %d %H:%M:%S %Y")


def _parse_estimated_hour(tweet):
    match = re.search(r'\d{2}:\d{2}', tweet['text'].replace('h',':'))
    if match:
        return match.group()
    match = re.search(r'\d{2}h', tweet['text'])    
    if match:
        return match.group()
    return tweet['text'].split(ESTIMATION)[-1].encode('utf-8')
    

class Event(object):
    
    
    def __init__(self, end_tweet):
        self.end_tweet = end_tweet
        self.start_tweet = None
        self.estimation_tweet = None
    
    def is_closed(self):
        return self.start_tweet is not None
    
    def close(self, start_tweet):
        self.start_tweet = start_tweet
    
    def get_cause(self):
        for cause, keyw in causes.iteritems():
            if cause in self.start_tweet['text'].encode('utf-8'):
                return keyw
        return "UNKNOWN"
    
    def get_start_hour(self):
        return _parse_date(self.start_tweet).hour
    
    def set_estimation(self, estimation_tweet):
        self.estimation_tweet = estimation_tweet
    
    def get_duration(self):
        start_time = _parse_date(self.start_tweet)
        end_time = _parse_date(self.end_tweet)
        if start_time.day == end_time.day:
            return end_time - start_time
        return None
    
    def get_string(self):
        out = ""
        if self.is_closed():
            out = "{} - {} \n Start At {} with:\n {}\n".format(self.get_cause(),
                                             self.get_duration(),
                                             self.start_tweet['created_at'],
                                             self.start_tweet['text'].encode('utf-8'))
        if self.estimation_tweet is not None:                                         
            out += "Expected end at {}\n".format(_parse_estimated_hour(self.estimation_tweet))
        out += "Ends At {} with:\n {}\n\n".format(self.end_tweet['created_at'],
                                       self.end_tweet['text'].encode('utf-8'))
        return out

    def to_obj(self):
        obj = {"duration":self.get_duration().seconds, "cause":self.get_cause(),
               "start_date":self.start_tweet['created_at'],
               "end_date":self.end_tweet['created_at'],
               "start_tweet": self.start_tweet['text'].encode('utf-8'),
               "end_tweet": self.end_tweet['text'].encode('utf-8')}
        return obj
        
    def __repr__(self):
        return self.get_string()


class EventCollection(object):
    """handles a collection of events"""
    
    def __init__(self, eventlist):
        self.eventlist = eventlist
        
    def add(self, event):
        if not isinstance(event, Event):
            raise TypeError("only event objects accepted")
        self.eventlist.append(event)
    
    def save(self, outputfile):
        """ saves to outpufile """
        
        with open(outputfile, 'w') as outf:
            outf.write(json.dumps([t.to_obj() for t in self.eventlist]))
        
    def get_durations_by_cause(self):
        durations_by_cause = {k:[] for k in causes.values()}
        durations_by_cause['UNKNOWN'] = []
        for event in self.eventlist:
            if event.get_duration():
                durations_by_cause[event.get_cause()].append(event.get_duration()) 
        return durations_by_cause
    
    def get_durations_by_time(self):
        durations_by_time = {k:[] for k in range(24)}
        
        for event in self.eventlist:
            durations_by_time[event.get_start_hour()].append(event.get_duration()) 
        return durations_by_time
    
    
    def __repr__(self):
        return '\n'.join([e.get_string() for e in self.eventlist])