import pandas as pd

import process_twitter

def filter_rep_tweet_words(rep_twitter_json, update):
    '''
    Preprocess tweet text into a cleaned list of words

    Inputs:
        tweet: a tweet (dictionary)
        stop_words_bool: boolean, True if you want to remove STOP_WORDS

    Returns: a tuple of cleaned words
    '''
    with open(rep_twitter_json) as ji:
        json_str = ji.read()
        rep_dict json.loads(json_str)

    reps_twitter = get_twitter_handles('illinois_reps_twitter_handles.txt')

    write_type = 'w'
    if update and path.exists('reps_cleaned.csv'):
        write_type = 'a'

    with open('reps_cleaned.csv', write_type) as c:
        f = csv.writer(c)
        if write_type == 'w':
            f.writerow(["rep_name", "tweet_id", "hashtag", "user_mentions"])
        for rep in rep_dict:
            for tweet in rep_dict[rep]['tweets']:
                text = rep_dict[rep]['tweets'][tweet]['text'].encode('ascii', 'ignore').decode('ascii') # remove emojis etc
                hashtags = re.findall(r"#(\w+)", text)
                mentions = [m for m in re.findall(r"@(\w+)", text) if m not in reps_twitter]
                f.writerow([rep, tweet, hashtags, mentions])

def generate_joined_table(topics_df, csv):
    '''
    '''
    df = pd.read_csv(csv, dtype={'bill_number':str})
    joined = pd.merge(df, topics_df, on=['bill_number'])
    return joined

def main(topics_csv, users_csv, hashtags_csv):
    '''
    '''
    topics = pd.read_csv(topics_csv, dtype={'bill_number':str})
    topics.dropna(subset=['topic'], inplace=True)
    users = generate_joined_table(topics, users_csv).groupby(['user', 'topic']).sum()
    hashtags = generate_joined_table(topics, hashtags_csv).groupby(['hashtag','topic']).count()

    reps_filtered = pd.read_csv('reps_cleaned.csv')
    
