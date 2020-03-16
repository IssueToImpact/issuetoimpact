import json
from datetime import datetime

from get_twitter_data.standard_twitter_search import twitter_search

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
        bills = json.loads(json_str)

    date_since = datetime.strptime('1/1/2020', '%m/%d/%Y')

    active_bills = {b: bills[b]['short_description'] for b in bills
                       if bills[b]['committee']!=None and
                            datetime.strptime(bills[b]['last_action']['date'],
                                              '%m/%d/%Y') >= date_since}

    return list(active_bills.keys())

def update_tweet_dict(tweet_json, bill_num, tweet_dict):
    '''
    Update tweet dictionary with tweet information
    Inputs:
        tweet_json (json): response from twitter api
        bill_num (str): bill number
        tweet_dict (dict): the dictionary to be updated
    '''
    if bill_num not in tweet_dict:
        tweet_dict[bill_num] = {}

    tweet_id = tweet_json['id']
    if tweet_id not in tweet_dict[bill_num]:
        tweet = {key: tweet_json[key] for key in ['full_text', 'created_at']}
        tweet['user'] = tweet_json['user']['name']
        tweet['url'] = 'https://twitter.com/{}/status/{}'\
                        .format(tweet_json['user']['screen_name'], tweet_id)
        tweet_dict[bill_num][tweet_id] = tweet

def update_users_dict(tweet_json, bill_num, users_dict):
    '''
    Update users dictionary with tweet information
    Inputs:
        tweet_json (json): response from twitter api
        bill_num (str): bill number
        users_dict (dict): the dictionary to be updated
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

def get_data_from_tweet(tweets, bill_num, tweet_dict, users_dict):
    '''
    '''
    if tweets['statuses']:
        for t in tweets['statuses']:
            update_tweet_dict(t, bill_num, tweet_dict)
            update_users_dict(t, bill_num, users_dict)

def save_to_json_file(dict, output_filename):
    '''
    Save dictionary to json file
    Inputs:
        dict: the dict to save
        output_filename: the file to create
    '''
    with open(output_filename, 'w') as output_file:
        json.dump(dict, output_file)

def search_bill_tweets(bill_info_file, limit, print_to_screen, tweet_json_file='data/bill_info.json', users_json_file='data/users_info.json'):
    '''
    Search tweets referencing bill numbers in illinois
    Inputs:
        tweet_json_file (str): output filename for tweets file
        bill_info_file (str): output filename for users file
    Returns:
        generates tweets and users json file
    '''
    tweet_dict = {}
    users_dict = {}

    active_bills = find_active_bills(bill_info_file)

    if limit:
        active_bills = active_bills[:limit]

    for i, bill_num in enumerate(active_bills):
        tweets_json = twitter_search(bill_num, i, 'bills')
        if print_to_screen and i == 0:
            print(json.dumps(tweets_json, indent=2))
        if not tweets_json:
            break
        get_data_from_tweet(tweets_json, bill_num, tweet_dict, users_dict)

    save_to_json_file(tweet_dict, tweet_json_file)
    save_to_json_file(users_dict, users_json_file)
