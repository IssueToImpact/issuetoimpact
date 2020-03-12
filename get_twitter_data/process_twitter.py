import json
import csv

from rep_twitter_search import get_twitter_handles

def open_json(filename):
    '''
    '''
    with open(filename) as ji:
        json_str = ji.read()
        return json.loads(json_str)

def filter_users(users_filename):
    '''
    '''
    reps_twitter = get_twitter_handles('illinois_reps_twitter_handles.txt')

    users_dict = open_json(users_filename)
    illinois_list = ['IL', 'Il', 'Illinois', 'illinois', 'Chicago', 'chicago']
    il_users = set()
    for b in users_dict:
        for user in users_dict[b]:
            if any(il in users_dict[b][user]['location'] for il in illinois_list) or\
            users_dict[b][user]['screen_name'] in reps_twitter.keys():
                il_users.add(users_dict[b][user]['name'])
    return il_users

def write_bill_csv(tweet_filename, users_filename):
    '''
    '''
    il_users = filter_users(users_filename)
    tweet_dict = open_json(tweet_filename)

    with open('tweets.csv', 'w') as c:
        f = csv.writer(c)
        f.writerow(["bill_num", "tweet_id", "text", "date", "user", "url"])
        for b in tweet_dict:
            for tweet in tweet_dict[b]:
                if tweet_dict[b][tweet]["user"] in il_users:
                    f.writerow([b, tweet, tweet_dict[b][tweet]["text"].strip().replace("\n", ""),
                        tweet_dict[b][tweet]["created_at"],
                        tweet_dict[b][tweet]["user"],
                        tweet_dict[b][tweet]["url"]])
