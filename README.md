# issuetoimpact

This project aims to increase participation in democracy by making issue/legislation advocacy easy and quick for political non-experts.

Our platform allows a user to search for active legislation by topic and provides all the information needed to gain a basic understanding of the legislation and then contact their representative.

We combine information from the Illinois General Assembly website with mentions on Twitter along with the contact information for relevant representatives based on the user's location and a generic template for what to write/say. Users can also search for their representative and get back basic information about their record.

## Getting started

Run `source install.sh` to set up virtual environment

`main.py` is the entry point for the application.

## Front end

Our platform is a Django user interface which connects to a sqlite database and queries based on various filters provided by the user.

Users can enter search terms and/or select which topics they want to search by. Our platform queries the database, and displays bills relevant to the search criteria entered as well as relevant tweets pertaining to that bill (if relevant tweets exist).
To provide the user with their representatives’ contact information, the user enters  an address and we connect to the Open States API and return representatives and their contact info (address, phone number, email) as well as some analysis on their bill sponsorship and legislation pass rate.

### To test:

## Back end

Our backend code consists of modules for scraping data from the Illinois General website (scraper.py), searching Twitter (get_twitter_data.py), aggregating the data (process.py) and creating a sqlite database.  The script main.py is the entry point.

Command line arguments for main.py:
1. limit (int): set a limit for scraping and twitter api requests (e.g. 10)
2. print_to_screen (bool): print output to screen (to see each section is working)
3. load_from_json (bool): load from json instead of scraping

### To test:
* Scraping and twitter api: `python3 main.py 10 True False` will test both the scraper and twitter api search (limited to 10 requests) and print output to the
screen.  Note that with only 10 bills, the bill counts and other statistics for
each representative will be sparse.
* File and database making functionality - `python3 main.py None False True` will load the data from pre-existing json files, process and generate the sql database.
After running this you should be able to see that a database called IssuetoImpact.db
has been created along with several csv files that you can use to check that the
full legislation and representative data has been processed.


## Front end:
* Navigate to itoiUI directory
* Enter command `python3 runserver manage.py` (depending on your setup, you may need to run `python runserver manage.py`)
* If you get an error that a particular table does not exist, check that the 'IssuetoImpact.db' is at the same level of the directory as manage.py

# Example searches:
* Searching the keyword 'energy' should return a number of bills, including SB1781 which has tweets
* Searching the keyword 'voucher' should return a number of bills, including SB3416, which has tweets
* Two addresses with different reps are:
* 5300 S Shore Dr, Chicago, IL 60615
* 2825 S Archer Ave, Chicago, IL 60608
