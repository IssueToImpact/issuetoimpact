import json
import csv
import pandas as pd

import scraper
import process

BASE_URL = "http://www.ilga.gov"
LEG_URL = BASE_URL + "/legislation/"
senate_url = BASE_URL + "/senate/"
house_url = BASE_URL + "/house/"

def data_to_csv(data, filename, header):
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(data)

def get_bill_info(output_to_screen, load_from_json, limit):
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
    if not load_from_json:
        bill_links = scraper.get_bill_links(LEG_URL, BASE_URL, limit)
        bill_info = {}
        for link in bill_links:
            scraper.process_bill_link(link, bill_info)
        if not output_to_screen:
            with open('./data/bill_scraped_info.json', 'w') as f:
                json.dump(bill_info, f)

    else:
        with open("./data/bill_scraped_info.json", "r") as read_file:
            bill_info = json.load(read_file)

    return bill_info

def get_rep_info(output_to_screen, load_from_json):
    '''
    '''
    if not load_from_json:
        rep_info = {}
        scraper.update_rep_dict(rep_info, senate_url, 'Senate')
        scraper.update_rep_dict(rep_info, house_url, 'House')
        if not output_to_screen:
            with open('./data/rep_scraped_info.json', 'w') as f:
                json.dump(rep_info, f)
    else:
        with open("./data/rep_scraped_info.json", "r") as read_file:
            rep_info = json.load(read_file)

    return rep_info
#Process scraped bill data to add keywords, topic, and status to bill dictionary.
#Create lists that will go to csv files for sql database.
#Csv files created: bill_table_data.csv, bill_topics.csv, bill_keywords.csv
def output_bill_csvs(bill_info, rep_info, output_to_screen):
    '''
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

    if not output_to_screen:
        data_to_csv(bills_table_data, 'bill_table_data.csv', ['bill_number',
                                                          'chamber',
                                                          'status',
                                                          'last_action_date',
                                                          'topic',
                                                          'primary_sponsor',
                                                          'bill_url',
                                                          'synopsis'])
        data_to_csv(bill_keywords, 'bill_keywords.csv', ['keyword', 'bill_number'])
        data_to_csv(bill_topics, 'bill_topics.csv', ['bill_number', 'topic'])
    return (bills_table_data, bill_keywords, bill_topics)


def output_rep_stats_table(bill_info, rep_info, limit, output_to_screen):
    '''
    '''
    process.set_rep_bill_counts(bill_info, rep_info)

    rep_data = []
    for rep_name in rep_info.keys():
        process.rep_info_to_list(rep_info, rep_name, rep_data)

    rep_df = process.calc_rep_ranks(rep_data)
    print(rep_df)

    if not output_to_screen:
        rep_df.to_csv('rep_data.csv', index=False,
                      header = ['name',
                                'party',
                                'district',
                                'count_sponsored',
                                'count_passed',
                                'Agriculture',
                                'Budget',
                                'Commerce_and_Economic_Development',
                                'Criminal_Justice',
                                'Education',
                                'Energy_and_Public_Utilities',
                                'Environment',
                                'Health',
                                'Human_and_Social_Services',
                                'Employment_and_Labor',
                                'Public_Safety_and_Firearms',
                                'Regulation',
                                'Taxes',
                                'Telecommunications_and_Information_Technology',
                                'Transportation',
                                'Veterans_Affairs',
                                'pass_rate',
                                'sponsored_rank_in_party',
                                'pass_rate_rank_in_party'])

    return rep_df


def print_bill_info_to_screen(bill_info, limit):
    '''
    Prints bill information to screen.
    Inputs:
        limit - number of entries to print
    '''
    print("Basic dictionary of scraped bill info:")
    if limit:
        ct = 0
        for bill_number in bill_info.keys():
            print("Bill number: ", bill_number)
            print(bill_info[bill_number])
            print("\n\n")
            ct += 1
            if ct >= limit: break
    else:
        print(bill_info)

def print_bill_tables_to_screen(bills_table_data, bill_keywords, bill_topics, limit):
    '''
    Prints bill information , bill-keyword pairs, bill-topics to screen.
    Inputs:
        limit - number of entries to print
    '''
    print("Bills data:")
    print('Columns are: ["bill_number", "chamber", "status",\
                        "last_action_date", "topic", "primary_sponsor", \
                        "bill_url", "synopsis"]')
    print(bills_table_data[:10])
    print('\n\n')
    print("Bill-keyword pairs:")
    print(bill_keywords[:10])
    print('\n\n')

def print_rep_statistics(rep_info, limit):
    '''
    Prints representative info to screen.
    Inputs:
        limit - number of entries to print
    '''
    print("Dictionary of rep info:")
    if limit:
        ct = 0
        for rep_name in rep_info.keys():
            print("Rep Name: ", rep_name)
            print(rep_info[rep_name])
            print('\n\n')
            ct += 1
            if ct >= limit: break
    else:
        print(rep_info)

def get_legislation_data(limit, output_to_screen, load_from_json):
    '''
    Gets legislation data.
    If output_to_screen is True - prints data to screen (limit)
    If load_from_json is True - skips scraping Illinois General Assembly website
        and loads data from a json file.
    If load_from_json is False - scrapes info from Illinois General assembly
        website.
    '''
    # arg parse stuff

    if output_to_screen and not load_from_json:
        print("Scraping bill data...")

    bill_info = get_bill_info(output_to_screen, load_from_json, limit)

    if output_to_screen:
        print("Scraping reps data...")

    rep_info = get_rep_info(output_to_screen, load_from_json)

    if output_to_screen:
        print("Processing bill data...")

    bills_table_data, bill_keywords, bill_topics = output_bill_csvs(bill_info, rep_info, output_to_screen)

    rep_df = output_rep_stats_table(bill_info, rep_info, limit, output_to_screen)

    if output_to_screen:
        print_bill_info_to_screen(bill_info, limit)

        print("Rep data:")
        print(rep_df.head())

        print_bill_tables_to_screen(bills_table_data, bill_keywords, bill_topics, limit)
        print_rep_statistics(rep_info, limit)
