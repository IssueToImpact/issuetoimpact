import requests
import json
import time
from datetime import datetime

import credentials

def find_active_bills(bill_info_file):
    '''
    Generate list of bill numbers for bills that are active (have a committee
    and last date is within the past month)

    Inputs:
        bill_json_file (str): location of bill_info json file

    Returns:
        list of bill numbers
    '''
    with open(bill_info_file) as bi:
        json_str = bi.read()
        bill_dict = json.loads(json_str)

    date_since = datetime.strptime('1/1/2020', '%m/%d/%Y')

    active_bills = {b: bill_dict[b]['short description'] for b in bill_dict
                       if bill_dict[b]['committee']!=None and
                            datetime.strptime(bill_dict[b]['last action']['date'],
                                              '%m/%d/%Y') >= date_since}

    return list(active_bills.keys())

def call_twitter_api(bill_query_str):
    '''
    '''
    twitter_api = 'https://api.twitter.com/1.1/tweets/search/30day/prod.json'

    headers = {
        'authorization': credentials.TWITTER_HEADER_AUTH,
        'content-type': 'application/json',
    }

    data = '{{"query": "{} place:Illinois lang:en",\
                "maxResults":"100"}}'.format(bill_query_str)

    response = requests.post(twitter_api, headers=headers, data=data)

    response.raise_for_status()

    return response.json()


def update_tweet_dict(tweet_json, bill_num, tweet_dict):
    '''
    '''
    tweet_dict_keys = ['id', 'text', 'created_at']

    if bill_num not in tweet_dict:
        tweet_dict[bill_num] = []

    tweet = {key: tweet_json[key] for key in tweet_dict_keys}
    tweet['user'] = tweet_json['user']['name']
    if tweet_json['entities']:
        if tweet_json['entities']['urls']:
            tweet['url'] = tweet_json['entities']['urls'][0]['url']

    tweet_dict[bill_num].append(tweet)

def update_users_dict(tweet_json, bill_num, users_dict):
    '''
    '''
    users_dict_keys = ['id', 'name','screen_name', 'location', 'url', 'description']

    if bill_num not in users_dict.keys():
        users_dict[bill_num] = []

    user_dict = {key: tweet_json['user'][key] for key in users_dict_keys}
    users_dict[bill_num].append(user_dict)

    if 'retweeted_status' in tweet_json.keys():
        rt_user_dict = {key: tweet_json['retweeted_status']['user'][key] for key in users_dict_keys}
        users_dict[bill_num].append(rt_user_dict)

def search_bills(bill_info_file):
    '''
    '''
    tweet_dict = {}
    users_dict = {}
    bill_nums = find_active_bills(bill_info_file)

    for i, b in enumerate(bill_nums[:100]):
        if i != 0 and i % 12 == 0:  # rate limit = 12 rpm
            time.sleep(60)
        query_bill_str = '{} OR #{} '.format(b, b)
        tweets = call_twitter_api(query_bill_str)

        if tweets['results']:
            for t in tweets['results']:
                update_tweet_dict(t, b, tweet_dict)
                update_users_dict(t, b, users_dict)

    return (tweet_dict, users_dict)
