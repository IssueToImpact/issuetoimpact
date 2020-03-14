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


#Obtain a dictionary of basic bill info - either by scraping or from json.
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


#Obtain a dictionary of basic rep info - either by scraping or from json.
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


#Process scraped bill data to add keywords, topic, and status to bill dictionary.
#Create lists that will go to csv files for sql database.
#Csv files created: bill_table_data.csv, bill_topics.csv, bill_keywords.csv

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
