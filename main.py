import sys
import os
from os import path

sys.path.append('./legislation')
import Leg_Scraper

sys.path.append('/get_twitter_data')
from get_twitter_data import rep_twitter_search
from get_twitter_data import search_bills
from get_twitter_data import process_twitter

sys.path.append('/make_database')
from make_database import csv_to_sql_db

def go(limit, print_to_screen, load_from_json):
    '''
    The main entry point for the backend of the project. Scrape legislation and
    twitter data, process, and create sql database for use in UI

    Inputs:
        limit (int): limit scraper and search to entered number
        print_to_screen (bool): print limited output from each section to screen
        load_from_json (bool): run scraper from existing json file

    Returns:
        sql database with all legislation and twitter data for use in UI
    '''
    print("*** Running legislation scraper ***\n")
    Leg_Scraper.get_legislation_data(limit, print_to_screen, load_from_json)

    if not load_from_json:
        print("\n*** Searching twitter api for bill tweets ***\n")
        search_bills.search_bill_tweets('data/bill_scraped_info.json', limit, print_to_screen)

        print("\n*** Searching twitter api for reps tweets ***\n")
        rep_twitter_search.search_rep_twitter_data(limit, print_to_screen)

    print("\n*** Processing twitter data ***\n")
    process_twitter.generate_csvs(print_to_screen)

    print("\n*** Creating database ***")
    if path.exists('IssuetoImpact.db'):
        os.remove('IssuetoImpact.db')
    csv_to_sql_db.make_database('IssuetoImpact.db')
    print("Database created.")


if __name__=='__main__':
    limit = None
    print_to_screen = False
    load_from_json = False

    if len(sys.argv[1:]) == 3:
        limit = int(sys.argv[1])
        print_to_screen = (sys.argv[2] == 'True')
        load_from_json = (sys.argv[3] == 'True')
    else:
        print("Command line arguments not submitted, using defaults...")

    go(limit, print_to_screen, load_from_json)
