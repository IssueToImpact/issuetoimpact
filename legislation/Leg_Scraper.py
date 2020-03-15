import bs4
import requests
import html5lib
import time
import json
import csv
import re
import pandas as pd

import scraper
import process

#Parameters set by user
limit = None
output_to_file = True
output_to_screen = False
load_from_json = False

BASE_URL = "http://www.ilga.gov"
LEG_URL = BASE_URL + "/legislation/"
senate_url = BASE_URL + "/senate/"
house_url = BASE_URL + "/house/"

def data_to_csv(data, filename, header):
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(data)


'''
Scrape legislation information from Illinois General Assembly Website.
- If the parameter limit is not None, scraper will stop after collecting the number
specified in the limit parameter.
- If the parameter load_from_json is True, legislation and representative data
will not be scraped, instead it will be loaded from two json files called
'bill_scraped_info.json' and 'rep_scraped_info.json'.
- If the parameter output_to_file is True, legislation and representative data that
is scraped will be written out to json files called
'bill_scraped_info.json' and 'rep_scraped_info.json'.
- If the parameter output_to_screen is True, data that is scraped will be output
to the screen (with the limit specified).
'''
#Get legislation information
if not load_from_json:
    bill_links = scraper.get_bill_links(limit = limit)
    bill_info = {}

    for link in bill_links:
        scraper.process_bill_link(link, bill_info)

    if output_to_file:
        with open('bill_scraped_info.json', 'w') as f:
            json.dump(bill_info, f)

else:
    with open("bill_scraped_info.json", "r") as read_file:
        bill_info = json.load(read_file)


if output_to_screen and not load_from_json:
    print("Basic dictionary of scraped bill info:")
    if limit:
        ct = 0
        for bill_number in bill_info.keys():
            print("Bill number: ", bill_number)
            print(bill_info[bill_number])
            ct += 1
            if ct >= limit: break
    else:
        print(bill_info)


#Get representative information.
if not load_from_json:
    rep_info = {}
    scraper.update_rep_dict(rep_info, senate_url, 'Senate')
    scraper.update_rep_dict(rep_info, house_url, 'House')
    if output_to_file:
        with open('rep_scraped_info.json', 'w') as f:
            json.dump(rep_info, f)
else:
    with open("rep_scraped_info.json", "r") as read_file:
        rep_info = json.load(read_file)


'''
Process scraped bill data to add keywords, topic, and status to bill dictionary.
Create lists that will go to csv files for sql database.
If output_to_file parameter is True: csv files created: bill_table_data.csv,
    bill_topics.csv, bill_keywords.csv
If output_to_screen parameter is True, data will be printed on screen (up to limits
    if limit parameter is not None.)
'''

bills_table_data = []
bill_keywords = []
bill_topics = []
for bill_number in bill_info.keys():
    process.set_primary_sponsor(bill_info, bill_number, rep_info)
    process.set_keywords(bill_info, bill_number)
    process.set_topics(bill_info, bill_number)
    process.set_status(bill_info, bill_number)
    process.bill_info_to_list(bill_info, bill_number, bills_table_data)
    process.bill_keywords_to_list(bill_info, bill_number, bill_keywords)
    process.bill_topics_to_list(bill_info, bill_number, bill_topics)

if output_to_file:
    data_to_csv(bills_table_data, 'bill_table_data.csv', ['bill_number',
                                                      'chamber',
                                                      'status',
                                                      'last_action_date',
                                                      'topic',
                                                      'primary_sponsor',
                                                      'bill_url',
                                                      'synopsis'])
    data_to_csv(bill_keywords, 'bill_keywords.csv', ['bill_number', 'keyword'])
    data_to_csv(bill_topics, 'bill_topics.csv', ['bill_number', 'topic'])

if output_to_screen:
    print("Bills data:")
    print('Columns are: ["bill_number", "chamber", "status",\
                        "last_action_date", "topic", "primary_sponsor", \
                        "bill_url", "synopsis"]')
    print(bills_table_data[:limit])
    print('\n\n')
    print("Bill-keyword pairs:")
    print(bill_keywords[:limit])
    print('\n\n')
    print("Bill-topics:")
    print(bill_topics[:limit])


'''
Process scraped representative data to aggregate data from legislation data
to calculate metrics for each rep such as the number of bills sponsored, pass
rate of sponsored bills, and number of bills sponsored by topic.
Create list that will go to csv files for sql database.
If output_to_file parameter is True: csv file created: rep_data.csv
If output_to_screen parameter is True, data will be printed on screen (up to limits
    if limit parameter is not None.)
'''
process.set_rep_bill_counts(bill_info, rep_info)

if output_to_screen:
    print("Dictionary of rep info:")
    if limit:
        ct = 0
        for rep_name in rep_info.keys():
            print("Rep Name: ", rep_name)
            print(rep_info[rep_name])
            ct += 1
            if ct >= limit: break
    else:
        print(rep_info)

rep_data = []
for rep_name in rep_info.keys():
    process.rep_info_to_list(rep_info, rep_name, rep_data)

rep_df = process.calc_rep_ranks(rep_data)

if output_to_file:
    rep_df.to_csv('rep_data.csv', index=False)

if output_to_screen:
    print("Rep data:")
    print(rep_df.head(limit))
