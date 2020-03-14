import pandas as pd

import process_twitter

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

    return users, hashtags

def likelihood_tweets_keywords(rep_twitter_json):
    '''
    Given sample text from two speakers, and text from an unidentified speaker,
    return a tuple with the *normalized* log probabilities of each of the
    speakers uttering that text under a "k" order character-based Markov model,
    and a conclusion of which speaker uttered the unidentified text
    based on the two probabilities.
    '''
    filter_rep_tweet_words = process_twitter.filter_rep_tweet_words(rep_twitter_json)

    for tweet in tweets_top_k:
        likelihoods = []
        for topic, m in models.items():
            likelihoods.append((topic, m.log_probability(tweets_top_k[tweet])))
        tweet_likelihoods[tweet] = likelihoods
    return tweet_likelihoods
