import json
import csv
import re
import os.path
from os import path

from rep_twitter_search import get_twitter_handles

def open_json(filename):
    '''
    '''
    with open(filename) as ji:
        json_str = ji.read()
        return json.loads(json_str)

def generate_users_bills_table(users_filename, update):
    '''
    '''
    reps_twitter = get_twitter_handles('illinois_reps_twitter_handles.txt')

    users_dict = open_json(users_filename)
    illinois_list = ['IL', 'Il', 'Illinois', 'illinois', 'Chicago', 'chicago']

    write_type = 'w'

    if update and path.exists('users.csv'):
        write_type = 'a'

    with open('users.csv', write_type) as c:
        f = csv.writer(c)
        if write_type == 'w':
            f.writerow(["user", "bill_number", "count"])

        for b in users_dict:
            for user in users_dict[b]:
                if any(il in users_dict[b][user]['location'] for il in illinois_list) or\
                users_dict[b][user]['screen_name'] in reps_twitter.keys():
                    name = users_dict[b][user]['screen_name']
                    f.writerow([name, b, users_dict[b][user]['count']])

def write_bill_tweet_csv(bill_num, tweet_id, tweet, update):
    '''
    '''
    write_type = 'w'

    if update and path.exists('tweets.csv'):
        write_type = 'a'

    with open('tweets.csv', write_type) as c:
        f = csv.writer(c)
        if write_type == 'w':
            f.writerow(["bill_number", "tweet_id", "text", "date", "user", "url"])

        text = tweet["full_text"].strip().replace("\n", "")
        f.writerow([bill_num, tweet_id, text,
                    tweet["created_at"], tweet["user"],
                    tweet["url"]])

def write_bill_tweet_tables(tweet_json, update):
    '''
    '''
    tweet_dict = open_json(tweet_json)

    for bill_num in tweet_dict:
        for tweet in tweet_dict[bill_num]:
            write_bill_tweet_csv(bill_num, tweet_id, tweet, update)
            write_hashtag_csv(bill_num, tweet_dict[bill_num][tweet]["full_text"], update)


def write_hashtag_csv(bill_num, tweet_text, update):
    '''
    '''
    write_type = 'w'

    if update and path.exists('hashtags.csv'):
            write_type = 'a'

    with open('hashtags.csv', write_type) as c:
        f = csv.writer(c)
        if write_type == 'w':
            f.writerow(["bill_number", "hashtag"])

        hashtags = re.findall(r"#(\w+)", tweet_text)
        for h in hashtags:
            f.writerow([bill_num, h])
