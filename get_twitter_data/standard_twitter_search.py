import requests
import json
import time

TWITTER_HEADER_AUTH='Bearer AAAAAAAAAAAAAAAAAAAAAEqICgEAAAAAizW%2FPFWnJmhQ8%2FHTyOIjeHpm%2FK4%3Dc49oCSPRX8UDbCupscJiksNdMPZ2XjVGHN0GU3hQDEysYvcjXz'

def call_standard_twitter_api(query_str):
    '''
    '''
    twitter_standard_api = 'https://api.twitter.com/1.1/search/tweets.json'

    headers = {
        'authorization': credentials.TWITTER_HEADER_AUTH,
        'content-type': 'application/json'
    }

    data = {"q": "{} lang:en".format(query_str),\
            "maxResults":"100",
            "geocode": "40.005785,-88.429983,250mi",
            "tweet_mode": "extended"}
    response = requests.get(twitter_standard_api, headers=headers, params=data) # check this works!
    response.raise_for_status()

    return response.json()

def twitter_search(q, i, search_type='bills', full_search=False):
    '''
    '''

    if full_search == False and i >= 10:
        return None

    if i != 0 and i % 12 == 0:  # rate limit = 12 rpm
        print('sleeping...')
        time.sleep(60)

    if search_type == 'bills':
        query_str = '({} OR #{}) '.format(q, q)
    elif search_type == 'users':
        query_str = 'from: {} '.format(q)

    return call_standard_twitter_api(query_str)
