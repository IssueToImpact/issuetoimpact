import sys
import math
import process_twitter

class Markov:

    def __init__(self, list_words):
        '''
        Construct a new k-order Markov model using the statistics of string "s"
        '''
        self.freq_table = {}
        self.words = set()
        self.build_model(list_words)

    def build_model(self, word_list):
        '''
        '''
        for i, w in enumerate(word_list):
            if w not in self.words:
                self.words.add(w)

            if w not in self.freq_table:
                self.freq_table[w] = 1
            else:
                self.freq_table[w] += 1

    def log_probability(self, tweets_words):
        '''
        '''
        log_prob = 0
        for i, w in enumerate(tweets_words):
            log_prob += self.word_likelihood(w)
        return log_prob

    def word_likelihood(self, word):
        '''
        '''
        S = len(self.words)
        if word in self.freq_table:
            M = self.freq_table[word]
            prob = M/S
        else:
            prob = 0
        return prob

def likelihood_tweets_keywords(keywords_json, tweets_top_k):
    '''
    Given sample text from two speakers, and text from an unidentified speaker,
    return a tuple with the *normalized* log probabilities of each of the
    speakers uttering that text under a "k" order character-based Markov model,
    and a conclusion of which speaker uttered the unidentified text
    based on the two probabilities.
    '''
    keywords = process_twitter.filter_keywords(keywords_json)
    # rep_dict = process_twitter.filter_rep_tweet_words(rep_tweet_json)

    models = {}
    tweet_likelihoods = {}

    for topic in keywords:
        model = Markov(keywords[topic])
        models[topic] = model

    for tweet in tweets_top_k:
        likelihoods = []
        for topic, m in models.items():
            likelihoods.append((topic, m.log_probability(tweets_top_k[tweet])))
        tweet_likelihoods[tweet] = likelihoods
    return tweet_likelihoods
