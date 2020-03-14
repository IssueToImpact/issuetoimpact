
import json
import csv
import re
import pandas as pd

TOPICS = ['Agriculture', 'Budget', 'Commerce and Economic Development', 'Criminal Justice', 'Education',
          'Energy and Public Utilities', 'Environment', 'Health', 'Human and Social Services',
          'Employment and Labor', 'Public Safety and Firearms', 'Regulation', 'Taxes',
          'Telecommunications and Information Technology', 'Transportation', 'Veterans Affairs']

COMMITTEE_TOPICS = {'2549': 'Human and Social Services',
                    '2316': 'Agriculture',
                    '2331': 'Agriculture',
                    '2317': 'Budget',
                    '2329': 'Budget',
                    '2293': 'Education',
                    '2550': 'Budget',
                    '2293': 'Education',
                    '2294': 'Budget',
                    '2296': 'Education',
                    '2295': 'Human and Social Services',
                    '2297': 'Public Safety and Firearms',
                    '2551': 'Human and Social Services',
                    '2347': 'Regulation',
                    '2299': 'Regulation',
                    '2332': 'Regulation',
                    '2358': 'Commerce and Economic Development',
                    '2298': 'Commerce and Economic Development',
                    '2348': 'Regulation',
                    '2379': 'Telecommunications and Information Technology',
                    '2342': 'Criminal Justice',
                    '2381': 'Commerce and Economic Development',
                    '2318': 'Education',
                    '2361': 'Education',
                    '2300': 'Education',
                    '2355': 'Energy and Public Utilities',
                    '2343': 'Energy and Public Utilities',
                    '2344': 'Environment',
                    '2302': 'Regulation',
                    '2320': 'Regulation',
                    '2319': 'Regulation',
                    '2321': 'Commerce and Economic Development',
                    '2373': 'Employment and Labor',
                    '2304': 'Health',
                    '2349': 'Regulation',
                    '2333': 'Education',
                    '2330': 'Human and Social Services',
                    '2323': 'Regulation',
                    '2303': 'Commerce and Economic Development',
                    '2305': 'Education',
                    '2306': 'Human and Social Services',
                    '2552': 'Regulation',
                    '2335': 'Commerce and Economic Development',
                    '2345': 'Criminal Justice',
                    '2308': 'Criminal Justice',
                    '2362': 'Criminal Justice',
                    '2334': 'Employment and Labor',
                    '2309': 'Employment and Labor',
                    '2325': 'Regulation',
                    '2324': 'Regulation',
                    '2389': 'Health',
                    '2356': 'Budget',
                    '2644': 'Health',
                    '2310': 'Employment and Labor',
                    '2553': 'Health',
                    '2337': 'Health',
                    '2311': 'Energy and Public Utilities',
                    '2647': 'Public Safety and Firearms',
                    '2326': 'Taxes',
                    '2352': 'Budget',
                    '2611': 'Human and Social Services',
                    '2322': 'Regulation',
                    '2313': 'Regulation',
                    '2375': 'Telecommunications and Information Technology',
                    '2327': 'Transportation',
                    '2350': 'Transportation',
                    '2351': 'Transportation',
                    '2374': 'Veterans Affairs',
                    '2315': 'Veterans Affairs',
                    None: None}
INDEX_IGNORE = set(['a', 'also', 'an', 'and', 'are', 'as', 'at', 'be',
                    'but', 'by', 'code', 'for', 'from', 'government', 'how', 'i',
                    'ii', 'iii', 'in', 'is', 'not', 'of',
                    'on', 'or', 's', 'so', 'that', 'the', 'their', 'this', 'through', 'to',
                    'we', 'were', 'which', 'will', 'with', 'state',
                    'yet', 'amends', 'law', 'creates', 'illinois', 'act', 'state', '2019'])



def set_keywords(bill_info, bill_number):
    keyword_list = []
    terms = bill_info[bill_number]['short_description'].lower().split("-")
    words = []
    for term in terms:
            words.extend(term.split())
    first_sentence = bill_info[bill_number]['synopsis'].split(".")[0]
    words.extend(first_sentence.split())
    keywords = set()
    for word in words:
        word = word.lower().strip("&'$")
        if word not in INDEX_IGNORE:
            keywords.add(word)
    bill_info[bill_number]['keywords'] = list(keywords)


def set_status(bill_info, bill_number):
    last_action = bill_info[bill_number]['last_action']['action']
    if last_action == 'Referred to Assignments':
        bill_status = 'In process - not yet assigned to committee'
    elif last_action.startswith("Public Act"):
        bill_status = 'Passed and signed into law'
    else:
        bill_status = 'In process'
    bill_info[bill_number]['status'] = bill_status


def set_topics(bill_info, bill_number):
    bill_info[bill_number]['topic'] = COMMITTEE_TOPICS[
                                      bill_info[bill_number]['committee_id']]


def set_primary_sponsor(bill_info, bill_number, rep_info):
    chamber = 'senate' if bill_number.startswith('S') else 'house'
    primary_sponsor = bill_info[bill_number][chamber + '_sponsors'][0]
    party = rep_info[primary_sponsor]['party']
    bill_info[bill_number]['primary_sponsor'] = primary_sponsor + " (" + party + ")"

def set_rep_bill_counts(bill_info, rep_info):
    for bill_num, bill_dict in bill_info.items():
        sponsors = []
        if bill_dict['senate_sponsors']:
            sponsors.append(bill_dict['senate_sponsors'][0])
        if bill_dict['house_sponsors']:
            sponsors.append(bill_dict['house_sponsors'][0])
        for sponsor in sponsors:
            rep_info[sponsor]['bills']['ids'].append(bill_num)
            rep_info[sponsor]['bills']['count sponsored'] += 1
            if bill_dict['status'] == 'Passed and signed into law':
                rep_info[sponsor]['bills']['count passed'] += 1
            if bill_dict['committee']:
                topic = bill_dict['topic']
                if topic not in rep_info[sponsor]['bills']['topic counts']:
                    rep_info[sponsor]['bills']['topic counts'][topic] = 0
                rep_info[sponsor]['bills']['topic counts'][topic] += 1

def bill_info_to_list(bill_info, bill_number, bills_table_data):
    chamber = bill_info[bill_number]['last_action']['chamber']
    status = bill_info[bill_number]['status']
    topic = bill_info[bill_number]['topic']
    synopsis = bill_info[bill_number]['synopsis']
    primary_sponsor = bill_info[bill_number]['primary_sponsor']
    last_date = bill_info[bill_number]['last_action']['date']
    bill_url = bill_info[bill_number]['page_url']
    bills_table_data.append([bill_number,
                             chamber,
                             status,
                             last_date,
                             topic,
                             primary_sponsor,
                             bill_url,
                             synopsis])

def bill_keywords_to_list(bill_info, bill_number, bill_keywords):
    for keyword in set(bill_info[bill_number]['keywords']):
        bill_keywords.append([keyword, bill_number])

def bill_topics_to_list(bill_info, bill_number, bill_topics):
    bill_topics.append([bill_number, bill_info[bill_number]['topic']])

def rep_info_to_list(rep_info, rep_name, rep_data):
    rep_data_row = [rep_name,
                     rep_info[rep_name]['party'],
                     rep_info[rep_name]['district'],
                     rep_info[rep_name]['bills']['count sponsored'],
                     rep_info[rep_name]['bills']['count passed']]

    for topic in TOPICS:
        vars()[topic + '_counts'] = 0
        if topic in rep_info[rep_name]['bills']['topic counts'].keys():
            vars()[topic + '_counts'] = rep_info[rep_name]['bills']['topic counts'][topic]
        rep_data_row.append(vars()[topic + '_counts'])
    rep_data.append(rep_data_row)


def calc_rep_ranks(rep_data):
    column_headers = {0:'name', 1:'party', 2:'district', 3:'count sponsored', 4:'count passed'}
    for i, topic in enumerate(TOPICS):
        column_headers[i+5] = topic
    rep_df = pd.DataFrame.from_records(rep_data)
    rep_df = rep_df.rename(columns = column_headers)
    rep_df['pass rate'] = 100*rep_df['count passed']/rep_df['count sponsored']
    rep_df = rep_df.fillna(0)
    ranks_sponsored = rep_df.groupby('party')['count sponsored'].rank(method='min', ascending=False).astype(int)
    ranks_sponsored.name = 'sponsored rank in party'
    rep_df = pd.concat([rep_df, ranks_sponsored], axis = 1)
    ranks_pass_rate = rep_df.groupby('party')['pass rate'].rank(method='min', ascending=False).astype(int)
    ranks_pass_rate.name = 'pass rate rank in party'
    rep_df = pd.concat([rep_df, ranks_pass_rate], axis = 1)
    return rep_df
