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

def make_request(count=200, max_id=None, target_user='@RERA_RATP'):
    dico_param = {'count':count,
                  'exclude_replies':True,
                  'user_id':target_user}
                  #'screen_name':target_user[1:]}
    if max_id:
        dico_param['max_id'] = max_id
    return api.request('statuses/user_timeline', params=dico_param)


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


def get_tweets_for_user(target_user='@RERA_RATP', n_rounds=100):
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
            
        r = make_request(max_id=max_id, target_user=target_user)
    return events        
    
def save_all(events, outputfile):
    """ saves to outpufile """
    with open(outputfile, 'w') as outf:
        outf.write(json.dumps([t.to_obj() for t in events]))
