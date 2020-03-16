import sys

sys.path.append('./legislation')
import Leg_Scraper

sys.path.append('/get_twitter_data')
from get_twitter_data import rep_twitter_search
from get_twitter_data import search_bills
from get_twitter_data import process_twitter

def go(argvs):
    '''
    '''
    limit = None
    print_to_screen = False
    load_from_json = False

    if len(argvs) == 3:
        limit = int(argvs[0])
        print_to_screen = argvs[1]
        load_from_json = argvs[2]
    elif len(argvs) != 0:
        return "please provide 3 arguments"

    if print_to_screen:
        print("*** Running legislation scraper ***\n")
    Leg_Scraper.get_legislation_data(limit, print_to_screen, load_from_json)

    if print_to_screen:
        print("\n*** Searching twitter api for bill tweets ***\n")
    search_bills.search_bill_tweets('data/bill_scraped_info.json', limit, print_to_screen)

    if print_to_screen:
        print("\n*** Searching twitter api for reps tweets ***\n")
    rep_twitter_search.search_rep_twitter_data(limit, print_to_screen)

    if print_to_screen:
        print("\n*** Processing twitter data ***\n")
    process_twitter.generate_csvs('./data/', print_to_screen)



if __name__=='__main__':
    go(sys.argv[1:])
