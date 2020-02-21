import requests

import credentials

headers = {
    'authorization': credentials.TWITTER_HEADER_AUTH,
    'content-type': 'application/json',
}

data = '{"query":"from: chicagotribune OR Chicago_Reader lang:en",\
        "maxResults": "10",\
        "fromDate":"201802010000",\
        "toDate":"201802282359"}'

response = requests.post('https://api.twitter.com/1.1/tweets/search/fullarchive/test.json', headers=headers, data=data)

response_output = response.json()
print(response_output)
