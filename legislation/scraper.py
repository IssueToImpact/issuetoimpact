import bs4
import requests
import html5lib
import time
import json
import csv
import re
import pandas as pd


BASE_URL = "http://www.ilga.gov"
LEG_URL = BASE_URL + "/legislation/"
senate_url = BASE_URL + "/senate/"
house_url = BASE_URL + "/house/"

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

def link_to_bs4(url):
    r = requests.get(url)
    html_text = r.text.encode('iso-8859-1')
    soup = bs4.BeautifulSoup(html_text, "html5lib")
    return soup


def get_bill_links(limit = None):
    #Get bs4 object from url
    soup = link_to_bs4(LEG_URL)

    #Scrape main pages and make a list of bill page links
    #If a limit is provided, only collect the links up to the limit
    main_links = soup.find_all("a")
    bill_links = []
    ct = 0
    for a in main_links:
        if a.has_attr("href") and a['href'].startswith('grplist.asp'):
            mid_url = LEG_URL + a['href']
            mid_r = requests.get(mid_url)
            mid_html_text = mid_r.text.encode('iso-8859-1')
            mid_soup = bs4.BeautifulSoup(mid_html_text, "html5lib")
            mid_links = mid_soup.find_all("a")
            for mid_a in mid_links:
                if mid_a.text.startswith("SB") or mid_a.text.startswith("HB"):
                    bill_url = BASE_URL + mid_a['href']
                    bill_links.append(bill_url)
                    ct += 1
                    if limit and ct >= limit: break
        if limit and ct >= limit: break
    return bill_links


def set_short_description(bs4_bill, bill_info, bill_number):
    heading_tags = bs4_bill.find_all('span', class_ = "heading2")
    for tag in heading_tags:
        if tag.text.startswith("Short Description"):
            description_tag = tag
    bill_short_descr = description_tag.next.next.next.text
    bill_info[bill_number]['short_description'] = bill_short_descr


def set_last_action_status(bs4_bill, bill_info, bill_number):
    heading_tags = bs4_bill.find_all('span', class_ = "heading2")
    for tag in heading_tags:
        if tag.text.startswith("Last Action"):
            last_action_marker = tag.next.next.next
            break
    last_action_tags = last_action_marker.find_all('td', class_ = "content")
    for tag in last_action_tags:
        if tag['align'] == 'left': last_action = tag.text
        if tag['align'] == 'right': last_action_date = tag.text.strip()
        if tag['align'] == 'center': last_action_chamber = tag.text
    bill_info[bill_number]['last_action'] = {'action': last_action,
                                             'date': last_action_date,
                                             'chamber': last_action_chamber}

def set_committee(bs4_bill, bill_info, bill_number):
    heading_tags = bs4_bill.find_all('span', class_ = "heading2")
    committee = None
    committee_id = None
    if bill_info[bill_number]['last_action']['action'] is not 'Referred to Assignments':
        for tag in heading_tags:
            if tag.text.startswith("Actions"):
                actions_tag = tag.next_sibling.next_sibling.next_sibling
        table_tags = actions_tag.find_all('td', align = "left")
        for i, tag in enumerate(table_tags):
            if tag.text.startswith("Assigned to"):
                committee_tag = tag
                committee_id = tag.a['href'][-4:]
                committee = tag.a.text
                break
    bill_info[bill_number]['committee_id'] = committee_id
    bill_info[bill_number]['committee'] = committee

def set_sponsors(bs4_bill, bill_info, bill_number, chamber):
    heading_tags = bs4_bill.find_all('span', class_ = "heading2")
    next_tag = None
    for tag in heading_tags:
        if tag.text.startswith(str(chamber) + " Sponsors"):
            next_tag = tag.next_sibling.next_sibling
            break
    sponsors = []
    while True:
        if next_tag is None: break
        if isinstance(next_tag, bs4.element.Tag) and next_tag.has_attr("href"):
            sponsors.append(next_tag.text)
        next_tag = next_tag.next_sibling
        if next_tag in heading_tags: break
    bill_info[bill_number][str(chamber).lower() + '_sponsors'] = sponsors

def set_synopsis(bs4_bill, bill_info, bill_number):
    synopsis_list = []
    for tag in bs4_bill.find_all('span', class_ = "content notranslate"):
        synopsis_list.append(tag.text.strip())
    synopsis = "  ".join(synopsis_list)
    bill_info[bill_number]['synopsis'] = synopsis.strip()



def process_bill_link(url, bill_info):
    bs4_bill = link_to_bs4(url)

    #Add bill number
    bill_number = bs4_bill.title.text.split()[-1]
    bill_info[bill_number] = {}

    bill_info[bill_number]['page_url'] = url
    set_short_description(bs4_bill, bill_info, bill_number)
    set_last_action_status(bs4_bill, bill_info, bill_number)
    set_committee(bs4_bill, bill_info, bill_number)
    set_sponsors(bs4_bill, bill_info, bill_number, 'Senate')
    set_sponsors(bs4_bill, bill_info, bill_number, 'House')
    set_synopsis(bs4_bill, bill_info, bill_number)

def update_rep_dict(rep_info, url, chamber):
    soup = link_to_bs4(url)
    tablerow_tags = soup.find_all('td', class_ = "detail")
    for i in range(0,len(tablerow_tags),5):
        name = tablerow_tags[i].a.text
        rep_info[name] = {}
        committees_link = url + tablerow_tags[i+2].a["href"]
        district = tablerow_tags[i+3].text
        party = tablerow_tags[i+4].text
        rep_info[name]['party'] = party
        rep_info[name]['district'] = str(chamber) + ' ' + str(district)
        rep_info[name]['committees'] = []

        #Go to committees page and grab committees
        committee_soup = link_to_bs4(committees_link)
        com_table_tags = committee_soup.find_all('td', class_="billlist")
        for tag in com_table_tags:
            if tag.a and 'hearing' in tag.a['href']:
                committee_id = re.findall(r'ID=([\d]{4})', tag.a['href'])[0]
                rep_info[name]['committees'].append((tag.text.strip(), committee_id))
        rep_info[name]['bills'] = {'ids': [], 'count sponsored': 0, 'count passed': 0, 'topic counts':{}}
