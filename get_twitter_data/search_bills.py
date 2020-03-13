import json
from datetime import datetime

from standard_twitter_search import twitter_search

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

def get_data_from_tweet(tweets, bill_num, tweet_dict, users_dict):
    '''
    '''
    if tweets['statuses']:
        for t in tweets['statuses']:
            update_tweet_dict(t, bill_num, tweet_dict)
            update_users_dict(t, bill_num, users_dict)

def update_tweet_dict(tweet_json, bill_num, tweet_dict):
    '''
    '''

    if bill_num not in tweet_dict:
        tweet_dict[bill_num] = {}

    tweet_id = tweet_json['id']
    if tweet_id not in tweet_dict[bill_num]:
        tweet = {key: tweet_json[key] for key in ['full_text', 'created_at']}
        tweet['user'] = tweet_json['user']['name']
        tweet['url'] = twitter_url = 'https://twitter.com/{}/status/{}'.format(tweet_json['user']['screen_name'], tweet_id)
        tweet_dict[bill_num][tweet_id] = tweet

def update_users_dict(tweet_json, bill_num, users_dict):
    '''
    '''
    users_dict_keys = ['name','screen_name', 'location', 'description']

    if bill_num not in users_dict:
        users_dict[bill_num] = {}

    user_id = tweet_json['user']['id']
    if user_id not in users_dict[bill_num]:
        user_dict = {key: tweet_json['user'][key] for key in users_dict_keys}
        user_dict['count'] = 1
        users_dict[bill_num][user_id] = user_dict
    else:
        users_dict[bill_num][user_id]['count'] += 1

def save_to_json_file(dict, output_filename):
    '''
    '''
    with open(output_filename, 'w') as output_file:
        json.dump(dict, output_file)

def search_bill_tweets(bill_info_file, tweet_json_file, users_json_file):
    '''
    '''
    tweet_dict = {}
    users_dict = {}

    active_bills = find_active_bills(bill_info_file)
    for i, bill_num in enumerate(active_bills):
        tweets_json = twitter_search(bill_num, i, 'bills', True)
        if not tweets_json:
            break
        get_data_from_tweet(tweets_json, bill_num, tweet_dict, users_dict)

    save_to_json_file(tweet_dict, tweet_json_file)
    save_to_json_file(users_dict, users_json_file)
