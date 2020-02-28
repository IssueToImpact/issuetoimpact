import requests
import json

import credentials

tweet_dict = {}
users_dict = {}

headers = {
    'authorization': credentials.TWITTER_HEADER_AUTH,
    'content-type': 'application/json',
}
data_str = '{"query": "HB3493 #HB3493 place: Illinois lang:en",\
            "maxResults":"100",\
            "fromDate":"202002010000",\
            "toDate":"202002270000"}'

with open('../bill_info.json') as bf:
    json_str = bf.read()
    bill_dict = json.loads(json_str)

bill_nums = list(bill_dict.keys())
#
# for i in range(0, len(bill_nums), 8):
#     bill_num_block = bill_nums[i: i+8]
#     search_bills_str = " OR ".join(bill_num_block)
#     # data['query'] = search_bills_str
#     # data['query'] = 'SB001'
#     #
#     # data_str = str(data)
#     print(data_str)

bill_num = 'HB3493'
response = requests.post('https://api.twitter.com/1.1/tweets/search/fullarchive/test.json', headers=headers, data=data_str)

response_output = response.json()
users_dict_keys = ['id', 'name','screen_name', 'location', 'url', 'description']

for tweet in response_output['results']:
    id = tweet['id']
    tweet_dict[id] = {}
    tweet_dict[id]['text'] = tweet['text']
    tweet_dict[id]['user'] = tweet['user']['name']
    tweet_dict[id]['bill'] = bill_num
    tweet_dict[id]['timestamp'] = tweet['created_at']
    if tweet['entities']['urls']:
        tweet_dict[id]['url'] = tweet['entities']['urls'][0]['url']


    if bill_num not in users_dict.keys():
        users_dict[bill_num] = []
    user_dict = {key: tweet['user'][key] for key in users_dict_keys}
    users_dict[bill_num].append(user_dict)

    if 'retweeted_status' in tweet.keys():
        rt_user_dict = {key: tweet['retweeted_status']['user'][key] for key in users_dict_keys}
        users_dict[bill_num].append(rt_user_dict)
