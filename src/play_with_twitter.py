# -*- coding: utf-8 -*-
"""
Created on Wed Oct 12 16:28:29 2016

@author: manu
"""

from credentials import oauth_consumer_key, oauth_consumer_secret, oauth_token, oauth_secret

from TwitterAPI import TwitterAPI
api = TwitterAPI(oauth_consumer_key, oauth_consumer_secret, oauth_token, oauth_secret)
from datetime import datetime
import json

def make_request(count=200, max_id=None, target_user='@RERA_RATP'):
    dico_param = {'count':count,
                  'exclude_replies':True,
                  'user_id':target_user,
                  'screen_name':target_user[1:]}
    if max_id:
        dico_param['max_id'] = max_id
    return api.request('statuses/user_timeline', dico_param)


interrupted_traffic = []
perturbed_traffic = []
rame_stationne = []
end_incident = []
police_intervention = []
travaux = []
estimation = []
incident_types = {}

causes = {"panne de signalisation":"PANNE SIG",
          "panne de matériel":"PANNE MAT",
          "panne électrique":"PANNE ELEC",
          "voyageur sur la voie":"VOYAGEUR_VOIE",
          "malaise voyageur":"VOYAGEUR_MALAISE",
          "colis suspect": "COLIS"}


def parse_tweet(tweet):
    """ parse the twee, returns the date, type of event"""
    t = tweet['text'] 
    typ = "other"
    nature = 'unknown'
    if "trafic est perturb" in t:
        nature = 'perturbed_traffic'
        typ = "start"
    elif "la rame stationne" in t:
        nature = 'rame_stationne'
        
    elif "Reprise estim" in t:
        nature = 'estimation'
        
    elif "police" in t:
        nature = 'police_intervention'
        
    elif "Retour " in t and " un trafic " in t:
        nature = 'end_incident'
        typ = "end"
    print tweet['created_at'], nature, typ
    return tweet['created_at'], nature, typ

def _parse_date(tweet):
    return datetime.strptime(tweet['created_at'].replace('+0000 ','')
                                       , "%a %b %d %H:%M:%S %Y")

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

def get_tweets_for_user(target_user='@RERA_RATP', n_rounds=100):
    """ get it all """
    r = make_request(target_user=target_user)
    events = []
    current_event = None
    for _ in range(n_rounds):
        for item in r:
            #print item['created_at']
            max_id = item['id']
            date, nature, typ = parse_tweet(item)
            if typ == 'end':            
                current_event = Event(item)
            if typ =='start' and current_event:
                current_event.close(item)
                events.append(current_event)
            
        r = make_request(max_id=max_id, target_user=target_user)
    return events        
    
def save_all(events, outputfile):
    """ saves to outpufile """
    with open(outputfile, 'w') as outf:
        
        outf.write(json.dumps([t.to_obj() for t in events]))

import os.path as op
outputfile = op.join('C:/Users/Manu/workspace/ratp_traffic/src',
                     'saved_tweets.json')
events = get_tweets_for_user(n_round=10)
save_all(events, outputfile)
