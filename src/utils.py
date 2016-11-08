# -*- coding: utf-8 -*-
"""
Created on Mon Nov 07 23:26:06 2016

@author: Manu
"""

from credentials import oauth_consumer_key, oauth_consumer_secret, oauth_token, oauth_secret

from TwitterAPI import TwitterAPI
api = TwitterAPI(oauth_consumer_key, oauth_consumer_secret, oauth_token, oauth_secret)
import json
from event import Event, EventCollection
from constants import ESTIMATION



def make_request(count=200, max_id=None, target_user='@RER_A'):
    dico_param = {'count':count,
                  'exclude_replies':True,
                  'user_id':target_user,
                  'screen_name':target_user[1:]}
    if max_id:
        dico_param['max_id'] = max_id
    return api.request('statuses/user_timeline', params=dico_param)


def parse_tweet(tweet):
    """ parse the twee, returns the date, type of event"""
    t = tweet['text'] 
    typ = "other"
    nature = 'unknown'
    if "trafic est perturb" in t or 'trafic est ralenti' in t:
        nature = 'perturbed_traffic'
        typ = "start"
    elif "trafic est interrompu" in t:
        nature = 'interrupted_traffic'
        
    elif "la rame stationne" in t:
        nature = 'rame_stationne'
        
    elif "Reprise estim" in t:
        nature = ESTIMATION
        
    elif "police" in t:
        nature = 'police_intervention'
        
    elif "Retour " in t and " un trafic " in t:
        nature = 'end_incident'
        typ = "end"
#    if typ=='other':
#        print tweet['created_at'], nature, typ, t
    return tweet['created_at'], nature, typ


def get_tweets_for_user(target_user, n_rounds=100):
    """ get it all """
    r = make_request(target_user=target_user)
    events = EventCollection([])
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
                events.add(current_event)
            if nature == ESTIMATION:
                
                current_event.set_estimation(item)
                print current_event
            
        r = make_request(max_id=max_id, target_user=target_user)
    return events        
    

