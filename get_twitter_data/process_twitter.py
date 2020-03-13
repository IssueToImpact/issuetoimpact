import json
import csv
import sys
import re
import unicodedata
import os.path
from os import path

from rep_twitter_search import get_twitter_handles

def keep_chr(ch):
    '''
    Find all characters that are classifed as punctuation in Unicode
    (except #, @, &) and combine them into a single string.
    '''

    return unicodedata.category(ch).startswith('P') and \
        ch not in ("#", "@", "&")

PUNCTUATION = " ".join([chr(i) for i in range(sys.maxunicode)
                        if keep_chr(chr(i))])

# When processing tweets, ignore these words
STOP_WORDS = ["i", "was" "a", "an", "the", "this", "that", "of", "for", "or", "by", "here"
              "and", "on", "to", "be", "if", "we", "you", "your", "in", "is",
              "at", "it", "rt", "mt", "with", "are", "from", "all", "than", "got"]

# When processing tweets, words w/ a prefix that appears in this list
# should be ignored.
STOP_PREFIXES = ("@", "http", "&amp")


def open_json(filename):
    '''
    '''
    with open(filename) as ji:
        json_str = ji.read()
        return json.loads(json_str)

# def filter_users(users_filename):
#     '''
#     '''
#     reps_twitter = get_twitter_handles('illinois_reps_twitter_handles.txt')
#
#     users_dict = open_json(users_filename)
#     illinois_list = ['IL', 'Il', 'Illinois', 'illinois', 'Chicago', 'chicago']
#     il_users = set()
#     for b in users_dict:
#         for user in users_dict[b]:
#             if any(il in users_dict[b][user]['location'] for il in illinois_list) or\
#             users_dict[b][user]['screen_name'] in reps_twitter.keys():
#                 il_users.add(users_dict[b][user]['name'])
#     return il_users

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

def write_reps_tweet_csv(reps_json, update):
    '''
    '''
    rep_dict = open_json(reps_json)

    write_type = 'w'
    if update and path.exists('reps_twitter.csv'):
        write_type = 'a'

    with open('reps_twitter.csv', write_type) as c:
        f = csv.writer(c)
        if write_type == 'w':
            f.writerow(["rep_name", "rep_twitter_handle", "tweet_id", "tweet_text", "url"])

        for r in rep_dict:
            for tweet in rep_dict[r]['tweets']:
                f.writerow([r, rep_dict[r]['twitter_handle'], tweet,
                           rep_dict[r]['tweets'][tweet]["text"].strip().replace("\n", ""),
                           rep_dict[r]['tweets'][tweet]["url"]])

def filter_rep_tweet_words(rep_twitter_json):
    '''
    Preprocess tweet text into a cleaned list of words

    Inputs:
        tweet: a tweet (dictionary)
        stop_words_bool: boolean, True if you want to remove STOP_WORDS

    Returns: a tuple of cleaned words
    '''
    rep_dict = open_json(rep_twitter_json)

    tweets = {}

    for rep in rep_dict:
        for tweet in rep_dict[rep]['tweets']:
            text = rep_dict[rep]['tweets'][tweet]['text'].encode('ascii', 'ignore').decode('ascii') # remove emojis etc
            words = text.split()
            processed_words = process_text(words)
            if not tweet in tweets:
                tweets[tweet] = processed_words
    return tweets


# def filter_keywords(keywords_json):
#     '''
#     '''
#     keywords_dict = open_json(keywords_json)
#
#     cleaned_keywords = {}
#
#     for topic in keywords_dict:
#         words = process_text(keywords_dict[topic])
#         if not topic in cleaned_keywords:
#             cleaned_keywords[topic] = words
#         else:
#             cleaned_keywords[topic].extend(words)
#     return cleaned_keywords


def process_text(words):
    '''
    '''

    cleaned_words = []
    for w in words:
        to_keep = True
        w = w.lower().strip().strip(PUNCTUATION)

        for c in w:
            if c.isdigit():
                to_keep = False

        if w in STOP_WORDS or len(w) == 1:
            to_keep = False

        for s in STOP_PREFIXES:
            if w.startswith(s):
                to_keep = False

        if to_keep and w != '':
            cleaned_words.append(w)
    return cleaned_words
