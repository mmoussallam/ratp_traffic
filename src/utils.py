# -*- coding: utf-8 -*-
"""
Created on Mon Nov 07 23:26:06 2016

@author: Manu
"""

from credentials import oauth_consumer_key, oauth_consumer_secret, oauth_token, oauth_secret

from TwitterAPI import TwitterAPI
api = TwitterAPI(oauth_consumer_key, oauth_consumer_secret, oauth_token, oauth_secret)
from event import Event, EventCollection, _parse_date
from constants import ESTIMATION
from pandas import DataFrame
import matplotlib.pyplot as plt

#r = api.request('search/tweets', params={'count':100, 'from':'RER_A'})

def get_user_id(target_user='@RER_A'):
    resp = api.request('users/show', params={'screen_name': target_user})
    obj = resp.json()
    return obj.get('id_str','')
    
def make_request(user_id, count=200, max_id=None,target_user=None):
    dico_param = {'count':count,
                  'exclude_replies':True,
                  'user_id':user_id}
                  
    if target_user and not user_id:
        dico_param['screen_name'] = target_user[1:]
        #dico_param['from'] = target_user[1:]
    if max_id:
        dico_param['max_id'] = max_id
    return api.request('statuses/user_timeline', params=dico_param)
    #return api.request('search/tweets', params=dico_param)


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


def get_tweets_for_user(target_user, n_rounds=16):
    """ get it all """
    user_id = get_user_id(target_user)
    r = make_request(int(user_id))
    #r = make_request(None, target_user=target_user)
    events = EventCollection([])
    event_stops = set([])
    current_event = None
    total=0
    for _ in range(n_rounds):
        for item in r:
            total+=1
            #print item['created_at']
            # if tweet is not on same day as current, close current and start again
            if current_event and _parse_date(item).day != _parse_date(current_event.end_tweet).day:
                current_event = None
            
            max_id = item['id']
            date, nature, typ = parse_tweet(item)
            if typ == 'end' and item['created_at'] not in event_stops :            
                current_event = Event(item)
                event_stops.add(item['created_at'])
            if typ =='start' and current_event:
                # add filter on same day otherwise seems absurd
                current_event.close(item)
                events.add(current_event)
                
            if nature == ESTIMATION and current_event:
                current_event.set_estimation(item)
                #print current_event
        print "new request", max_id, ' ', total," last tweet: ", item['text'], item['created_at']
        r = make_request(user_id, max_id=max_id)
        #r = make_request(None, max_id=max_id, target_user=target_user)
        
    print "%d tweets parsed" % total
    return events        
    

def print_stats(events, figure_path=None):
    """ compute stats """    
    # explore durations by causes
    durations_by_causes = events.get_durations_by_cause()
    df_causes = DataFrame( [{"cause":k, "duration":t.seconds / 3600.} for k,v in durations_by_causes.iteritems() for t in v])
    
    # explore durations by time
    durations_by_times = events.get_durations_by_time()
    df_times = DataFrame([{"time":k, "duration":t.seconds / 3600.} for k,v in durations_by_times.iteritems() for t in v])
    
    
    fig = plt.figure(figsize=(8,12))
    ax = plt.subplot(211)
    df_causes.boxplot(column='duration', by='cause', rot=75, ax=ax)
    ax = plt.subplot(212)
    df_times.boxplot(column='duration', by='time', ax=ax)
    fig.tight_layout()
    if figure_path:
        fig.savefig(figure_path)
    return figure_path