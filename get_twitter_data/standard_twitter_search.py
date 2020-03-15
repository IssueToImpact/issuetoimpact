import requests
import json
import time

TWITTER_HEADER_AUTH='Bearer AAAAAAAAAAAAAAAAAAAAAEqICgEAAAAAizW%2FPFWnJmhQ8%2FHTyOIjeHpm%2FK4%3Dc49oCSPRX8UDbCupscJiksNdMPZ2XjVGHN0GU3hQDEysYvcjXz'

def call_standard_twitter_api(query_str):
    '''
    Call twitter standard search api

    Inputs:
    '''
    twitter_standard_api = 'https://api.twitter.com/1.1/search/tweets.json'

    headers = {
        'authorization': TWITTER_HEADER_AUTH,
        'content-type': 'application/json'
    }

    data = {"q": "{} lang:en".format(query_str),\
            "maxResults":"100",
            "geocode": "40.005785,-88.429983,250mi",
            "tweet_mode": "extended"}
    response = requests.get(twitter_standard_api, headers=headers, params=data)
    response.raise_for_status()

    return response.json()

def twitter_search(st, i, search_type='bills'):
    '''
    Parse twitter query str and handle twitter rate limiting

    Inputs:
        st (string) input to call search api with
        i (int): index of the st in list to be called
        search_type (st): 'bills' or 'users' for different search queries
        full_search: run search of full list, or break after 10 calls

    Returns:
        twitter search api response (json)
        (breaks at i=10 when full_search is False)
    '''

    if i != 0 and i % 12 == 0:  # rate limit = 12 rpm
        print("Twitter search api rate limit...sleeping...")
        time.sleep(60)

    if search_type == 'bills':
        query_str = '({} OR #{}) '.format(st, st)
    elif search_type == 'users':
        query_str = 'from: {} '.format(st)

    return call_standard_twitter_api(query_str)
