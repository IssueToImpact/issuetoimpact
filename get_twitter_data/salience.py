'''
Algorithms for efficiently counting and sorting distinct `entities` or
unique values, are widely used in data analysis. Functions to
implement: count_tokens, find_top_k, find_min_count, find_frequent
'''

import math

import sys
import json

#Make lint be quiet.
#pylint: disable-msg=unused-argument, too-few-public-methods

def cmp_to_key(mycmp):
    '''
    Convert a cmp= function into a key= function
    From: https://docs.python.org/3/howto/sorting.html
    '''

    class CmpFn:
        '''
        Compare function class.
        '''
        def __init__(self, obj, *args):
            self.obj = obj
        def __lt__(self, other):
            return mycmp(self.obj, other.obj) < 0
        def __gt__(self, other):
            return mycmp(self.obj, other.obj) > 0
        def __eq__(self, other):
            return mycmp(self.obj, other.obj) == 0
        def __le__(self, other):
            return mycmp(self.obj, other.obj) <= 0
        def __ge__(self, other):
            return mycmp(self.obj, other.obj) >= 0
        def __ne__(self, other):
            return mycmp(self.obj, other.obj) != 0
    return CmpFn


def cmp_count_tuples(t0, t1):
    '''
    Compare pairs using the second value as the primary key and the
    first value as the secondary key.  Order the primary key in
    non-increasing order and the secondary key in non-decreasing
    order.

    Inputs:
        t0: pair
        t1: pair

    Returns: -1, 0, 1

    Sample uses:
        cmp(("A", 3), ("B", 2)) => -1

        cmp(("A", 2), ("B", 3)) => 1

        cmp(("A", 3), ("B", 3)) => -1

        cmp(("A", 3), ("A", 3))
    '''
    (key0, val0) = t0
    (key1, val1) = t1
    if val0 > val1:
        return -1

    if val0 < val1:
        return 1

    if key0 < key1:
        return -1

    if key0 > key1:
        return 1

    return 0


def sort_count_pairs(l):
    '''
    Sort pairs using the second value as the primary sort key and the
    first value as the seconary sort key.

    Inputs:
       l: list of pairs.

    Returns: list of key/value pairs
    '''
    return list(sorted(l, key=cmp_to_key(cmp_count_tuples)))


def get_json_from_file(filename):
    '''
    Read data from a JSON file.
    '''

    try:
        return json.load(open(filename))
    except OSError as e:
        print(e, file=sys.stderr)
        sys.exit(1)


def count_tokens(tokens):
    '''
    Counts each distinct token (item or entity) in a list of tokens

    Inputs:
        tokens: list of tokens (must be hashable/comparable)

    Returns: list (token, number of occurrences).
    '''

    token_count = {}

    for t in tokens:
        token_count[t] = token_count.get(t, 0) + 1

    return token_count.items()


def find_top_k(tokens, k):
    '''
    Find the k most frequently occurring tokens

    Inputs:
        tokens: list of tokens (must be hashable/comparable)
        k: a non-negative integer

    Returns: sorted list of the top k tuples
    '''

    # Error checking (DO NOT MODIFY)
    err_msg = "In find_top_k, k must be a non-negative integer"
    assert k >= 0, err_msg

    sorted_token_count = sort_count_pairs(count_tokens(tokens))

    return sorted_token_count[:k]


def find_min_count(tokens, min_count):
    '''
    Find the tokens that occur at least min_count times

    Inputs:
        tokens: a list of tokens (must be hashable/comparable)
        min_count: integer

    Returns: sorted list of tuples
    '''

    token_count = count_tokens(tokens)
    min_count_list = []

    for token in sort_count_pairs(token_count):
        if token[1] >= min_count:
            min_count_list.append(token)

    return min_count_list


def find_most_salient(tweets_dict, k):
    '''
    Find the k most salient tokens in each document

    Inputs:
        docs: a list of lists of tokens
        k: integer

    Returns: list of sorted list of tokens
     (inner lists are in decreasing order of tf-idf score)
    '''

    tf_idf = {}
    most_salient = {}
    tweets = list(tweets_dict.values())

    for tweet_id, tweet in tweets_dict.items():
        tf_idf[tweet_id] = {}

        for term in tweet:
            tf_idf[tweet_id][term] = (calculate_tf(tweet, term) *
                                   calculate_idf(tweets, term))

        sorted_terms = sort_count_pairs(tf_idf[tweet_id].items())
        most_salient[tweet_id] = [x[0] for x in sorted_terms][:k]

    return most_salient


def calculate_idf(tweets, term):
    '''
    Calculate the inverse document frequency of a term in a set of documents

    Inputs:
        docs: a list of lists of terms
        term: the term of interest

    Returns: idf (float) for the term in the set of docs
    '''

    term_in_docs = 0
    num_tweets = len(tweets)

    for tweet in tweets:
        if term in tweet:
            term_in_docs += 1
    idf = math.log(num_tweets / term_in_docs)

    return idf


def calculate_tf(doc, term):
    '''
    Calculate the term frequency of a term in a document

    Inputs:
        doc: a list of terms
        term: the term of interest

    Returns: the tf (float) for the term in the doc
    '''

    t_frequencies = count_tokens(doc)

    term_freq = dict(t_frequencies)[term]
    max_t_freq = find_top_k(doc, 1)

    tf = 0.5 + 0.5 * (term_freq / max_t_freq[0][1])

    return tf
