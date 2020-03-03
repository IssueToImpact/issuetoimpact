import requests
import json

import credentials

def find_active_bills(bill_info_file):
    '''
    Generate list of bill numbers for bills that are active (have a committee)

    Inputs:
        bill_json_file (str): location of bill_info json file

    Returns:
        list of bill numbers
    '''
    with open(bill_info_file) as bi:
        json_str = bi.read()
        bill_dict = json.loads(json_str)

    active_bills = {b: bill_dict[b]['short description'] for b in bill_dict
                       if bill_dict[b]['committee']!=None}

    return list(active_bills.keys())

def generate_bill_call_string(bill_block):
    '''
    '''
    assert len(bill_blocks) <= 5

    query_bills = bill_blocks + ['#' + x for x in bill_block]

    return ' OR '.join(query_bills)

def call_twitter_api(bill_num_list, bill_query_str):
    '''
    '''
    twitter_api = 'https://api.twitter.com/1.1/tweets/search/fullarchive/test.json'

    headers = {
        'authorization': credentials.TWITTER_HEADER_AUTH,
        'content-type': 'application/json',
    }

    data = '{{"query": "{} place: Illinois lang:en",\
                "maxResults":"100",\
                "fromDate":"202002010000",\
                "toDate":"202002270000"}}'.format(bill_query_str)

    response = requests.post(twitter_api, headers=headers, data=data)

    response_output = response.json()

    while 'next' in response_output:
        response = requests.post(twitter_api, headers=headers, data=data)

def search_bills(bill_info_file):
    '''
    '''
    bill_nums = find_active_bills(bill_info_file)

    for i in range(0, len(bill_nums), 5):
        bill_num_block = bill_nums[i: i+5]
        bill_query_str = generate_bill_call_string(bill_num_block)
        time.sleep(1/20)
        tweets = call_twitter_api(bill_query_str)


def update_tweet_dict(response_json):
    '''
    '''
    for tweet in response_output['results']:
        id = tweet['id']
        tweet_dict[id] = {}
        tweet_dict[id]['text'] = tweet['text']
        tweet_dict[id]['user'] = tweet['user']['name']
        tweet_dict[id]['bill'] = bill_num
        tweet_dict[id]['timestamp'] = tweet['created_at']
        if tweet['entities']['urls']:
            tweet_dict[id]['url'] = tweet['entities']['urls'][0]['url']


        if bill_num not in users_dict.keys():
            users_dict[bill_num] = []
        user_dict = {key: tweet['user'][key] for key in users_dict_keys}
        users_dict[bill_num].append(user_dict)

        if 'retweeted_status' in tweet.keys():
            rt_user_dict = {key: tweet['retweeted_status']['user'][key] for key in users_dict_keys}
            users_dict[bill_num].append(rt_user_dict)

def go(bill_info_file):
    '''
    '''
    tweet_dict = {}
    users_dict = {}





users_dict_keys = ['id', 'name','screen_name', 'location', 'url', 'description']
