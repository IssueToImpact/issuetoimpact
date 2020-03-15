import sqlite3
import pandas as pd
from pandas import DataFrame


filename = 'IssuetoImpact.db'

create_bills_table_sql = '''CREATE TABLE bills (
                        bill_number text PRIMARY KEY,
                        chamber text,
                        status text,
                        last_action_date text,
                        topic text,
                        primary_sponsor text,
                        bill_url text,
                        synopsis text);'''

create_bill_keywords_table_sql = '''CREATE TABLE bill_keywords (
                        bill_number text,
                        keyword text);'''

create_reps_table_sql = '''CREATE TABLE reps (
                        name text PRIMARY KEY,
                        party text,
                        district text,
                        count_sponsored integer,
                        count_passed integer,
                        Agriculture integer,
                        Budget integer,
                        Commerce_and_Economic_Development integer,
                        Criminal_Justice integer,
                        Education integer,
                        Energy_and_Public_Utilities integer,
                        Environment integer,
                        Health integer,
                        Human_and_Social_Services integer,
                        Employment_and_Labor integer,
                        Public_Safety_and_Firearms integer,
                        Regulation integer,
                        Taxes integer,
                        Telecommunications_and_Information_Technology integer,
                        Transportation integer,
                        Veterans_Affairs integer,
                        pass_rate float,
                        sponsored_rank_in_party integer,
                        pass_rate_rank_in_party integer);'''

create_tweets_table_sql = '''CREATE TABLE tweets (
                        bill_number text,
                        tweet_id text,
                        text text,
                        date text,
                        user text,
                        url text);'''


read_bills = pd.read_csv('bill_table_data.csv', header = 0)
read_bill_keywords = pd.read_csv('bill_keywords.csv')
read_reps = pd.read_csv('rep_data.csv', header = 0, usecols = range(1,24))
read_tweets = pd.read_csv('tweets.csv', header = 0)

conn = sqlite3.connect(filename)
c = conn.cursor()
c.execute(create_bills_table_sql)
c.execute(create_bill_keywords_table_sql)
c.execute(create_reps_table_sql)
c.execute(create_tweets_table_sql)

read_bills.to_sql('bills', conn, if_exists='append', index = False)
read_bill_keywords.to_sql('bill_keywords', conn, if_exists='append', index = False)
read_reps.to_sql('reps', conn, if_exists='append', index = False)
read_tweets.to_sql('tweets', conn, if_exists='append', index = False)
