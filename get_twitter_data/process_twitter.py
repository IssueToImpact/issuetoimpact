import json
import csv
import re
import os
from os import path

from get_twitter_data.rep_twitter_search import get_twitter_handles

DIR = os.path.dirname(os.path.abspath(__file__))

def open_json(filename):
    '''
    '''
    with open(filename) as ji:
        json_str = ji.read()
        return json.loads(json_str)

def generate_users_bills_table(users_filename):
    '''
    '''
    reps_twitter = get_twitter_handles()

    users_file =  os.path.join(DIR, users_filename)

    users_dict = open_json(users_filename)
    illinois_list = ['IL', 'Il', 'Illinois', 'illinois', 'Chicago', 'chicago']

    write_type = 'w'

    if path.exists('./data/users.csv'):
        write_type = 'a'

    with open('./data/users.csv', write_type) as c:
        f = csv.writer(c)
        if write_type == 'w':
            f.writerow(["user", "bill_number", "count"])

        for b in users_dict:
            for user in users_dict[b]:
                if any(il in users_dict[b][user]['location'] for il in illinois_list) or\
                users_dict[b][user]['screen_name'] in reps_twitter.keys():
                    name = users_dict[b][user]['screen_name']
                    f.writerow([name, b, users_dict[b][user]['count']])

def write_bill_tweet_csv(bill_num, tweet_id, tweet):
    '''
    '''
    write_type = 'w'

    if path.exists('./data/tweets.csv'):
        write_type = 'a'

    with open('./data/tweets.csv', write_type) as c:
        f = csv.writer(c)
        if write_type == 'w':
            f.writerow(["bill_number", "tweet_id", "text", "date", "user", "url"])

        text = tweet["full_text"].strip().replace("\n", "")
        f.writerow([bill_num, tweet_id, text,
                    tweet["created_at"], tweet["user"],
                    tweet["url"]])

def write_bill_tweet_tables(tweet_json):
    '''
    '''
    tweet_dict = open_json(tweet_json)

    for bill_num in tweet_dict:
        for tweet in tweet_dict[bill_num]:
            write_bill_tweet_csv(bill_num, tweet, tweet_dict[bill_num][tweet])
            write_hashtag_csv(bill_num, tweet_dict[bill_num][tweet]["full_text"])

def write_hashtag_csv(bill_num, tweet_text):
    '''
    '''
    write_type = 'w'

    if path.exists('hashtags.csv'):
        write_type = 'a'

    with open('hashtags.csv', write_type) as c:
        f = csv.writer(c)
        if write_type == 'w':
            f.writerow(["bill_number", "hashtag"])

        hashtags = re.findall(r"#(\w+)", tweet_text)
        for h in hashtags:
            f.writerow([bill_num, h])

def generate_csvs(output_path, print_to_screen):
    '''
    '''
    generate_users_bills_table(DIR + '/users.json')
    write_bill_tweet_tables(DIR +'/tweets.json')

    if print_to_screen:
        print("saving files:")
        print("   './data/tweets.csv'")
        print("   './data/users.csv'")
