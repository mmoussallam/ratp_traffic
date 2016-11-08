# -*- coding: utf-8 -*-
"""
Created on Mon Nov 07 23:27:32 2016

@author: Manu
"""
import json
from datetime import datetime

def _parse_date(tweet):
    return datetime.strptime(tweet['created_at'].replace('+0000 ','')
                                       , "%a %b %d %H:%M:%S %Y")

causes = {"panne de signalisation":"PANNE SIG",
          "panne de matériel":"PANNE MAT",
          "panne électrique":"PANNE ELEC",
          "voyageur sur la voie":"VOYAGEUR_VOIE",
          "malaise voyageur":"VOYAGEUR_MALAISE",
          "colis suspect": "COLIS"}

class Event(object):
    
    
    def __init__(self, end_tweet):
        self.end_tweet = end_tweet
        self.start_tweet = None
    
    def is_closed(self):
        return self.start_tweet is not None
    
    def close(self, start_tweet):
        self.start_tweet = start_tweet
    
    def get_cause(self):
        for cause, keyw in causes.iteritems():
            if cause in self.start_tweet['text'].encode('utf-8'):
                return keyw
        return "UNKNOWN"
        
    
    
    def get_duration(self):
        start_time = _parse_date(self.start_tweet)
        end_time = _parse_date(self.end_tweet)
        return end_time - start_time
    
    def get_string(self):
        out = ""
        if self.is_closed():
            out = "{} - {} \n Start At {} with:\n {}\n".format(self.get_cause(),
                                             self.get_duration(),
                                             self.start_tweet['created_at'],
                                             self.start_tweet['text'].encode('utf-8'))
        
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
        
    def get_statistics(self):
        durations_by_cause = {k:[] for k in causes.values()}
        
        for event in self.eventlist:
            durations_by_cause[event.get_cause()].append(event.get_duration()) 
        return durations_by_cause