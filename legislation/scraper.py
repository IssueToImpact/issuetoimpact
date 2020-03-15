import bs4
import requests
import html5lib
import re

def link_to_bs4(url):
    '''
    Converts url to a bs4 object.
    '''
    r = requests.get(url)
    html_text = r.text.encode('iso-8859-1')
    soup = bs4.BeautifulSoup(html_text, "html5lib")
    return soup

def get_bill_links(leg_url, base_url, limit=None):
    '''
    Goes to Illinois General Assembly website (LEG_URL) and puts direct links
    to bill pages into a list.  If limit is provided, only gathers specified
    number of links and then stops.
    Input:
        Optional limit (int)
    Output:
        list of urls (list of strings)
    '''
    #Get bs4 object from url
    soup = link_to_bs4(leg_url)

    #Scrape main pages and make a list of bill page links
    #If a limit is provided, only collect the links up to the limit
    main_links = soup.find_all("a")
    bill_links = []
    ct = 0
    for a in main_links:
        if a.has_attr("href") and a['href'].startswith('grplist.asp'):
            mid_url = leg_url + a['href']
            mid_r = requests.get(mid_url)
            mid_html_text = mid_r.text.encode('iso-8859-1')
            mid_soup = bs4.BeautifulSoup(mid_html_text, "html5lib")
            mid_links = mid_soup.find_all("a")
            for mid_a in mid_links:
                if mid_a.text.startswith("SB") or mid_a.text.startswith("HB"):
                    bill_url = base_url + mid_a['href']
                    bill_links.append(bill_url)
                    ct += 1
                    if limit and ct >= limit: break
        if limit and ct >= limit: break
    return bill_links


def set_short_description(bs4_bill, bill_info, bill_number):
    '''
    Given a bs4 object for a bill page, updates the short description of that
    bill number in the bill_info dictionary.
    Inputs:
        bs4_bill - bs4 object for a specific bill
        bill_info - dictionary of bill information that is modified in place
        bill_number - bill number (str - e.g. 'HB0001') corresponding to
                      bs4_bill object used as a key for the dictionary.
    Outputs:
        None - modifies the bill_info dictionary in place.
    '''
    heading_tags = bs4_bill.find_all('span', class_ = "heading2")
    for tag in heading_tags:
        if tag.text.startswith("Short Description"):
            description_tag = tag
    bill_short_descr = description_tag.next.next.next.text
    bill_info[bill_number]['short_description'] = bill_short_descr


def set_last_action_status(bs4_bill, bill_info, bill_number):
    '''
    Given a bs4 object for a bill page, updates the last action and
    status of that bill number in the bill_info dictionary.
    Inputs:
        bs4_bill - bs4 object for a specific bill
        bill_info - dictionary of bill information that is modified in place
        bill_number - bill number (str - e.g. 'HB0001') corresponding to
                      bs4_bill object used as a key for the dictionary.
    Outputs:
        None - modifies the bill_info dictionary in place.
    '''
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
    '''
    Given a bs4 object for a bill page, updates the committee (name and id) of
    that bill number in the bill_info dictionary.
    Inputs:
        bs4_bill - bs4 object for a specific bill
        bill_info - dictionary of bill information that is modified in place
        bill_number - bill number (str - e.g. 'HB0001') corresponding to
                      bs4_bill object used as a key for the dictionary.
    Outputs:
        None - modifies the bill_info dictionary in place.
    '''
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
    '''
    Given a bs4 object for a bill page, updates the sponsors of that
    bill number in the bill_info dictionary for the chamber specified.
    Inputs:
        bs4_bill - bs4 object for a specific bill
        bill_info - dictionary of bill information that is modified in place
        bill_number - bill number (str - e.g. 'HB0001') corresponding to
                      bs4_bill object used as a key for the dictionary.
        chamber - (str) either 'house' or 'senate'
    Outputs:
        None - modifies the bill_info dictionary in place.
    '''
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
    '''
    Given a bs4 object for a bill page, updates the synopsis of that
    bill number in the bill_info dictionary.
    Inputs:
        bs4_bill - bs4 object for a specific bill
        bill_info - dictionary of bill information that is modified in place
        bill_number - bill number (str - e.g. 'HB0001') corresponding to
                      bs4_bill object used as a key for the dictionary.
    Outputs:
        None - modifies the bill_info dictionary in place.
    '''
    synopsis_list = []
    for tag in bs4_bill.find_all('span', class_ = "content notranslate"):
        synopsis_list.append(tag.text.strip())
    synopsis = "  ".join(synopsis_list)
    bill_info[bill_number]['synopsis'] = synopsis.strip()


def process_bill_link(url, bill_info):
    '''
    Takes in a url for a specific bill page, obtains the bs4 object from the
    html, scrapes the bs4 object for basic bill info, and updates the bill_info
    dictionary with information about that bill.
    Modifies the dictionary in place with short description, last action,
        status, committee (if assigned), sponsors, and synopsis.
    '''
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
    '''
    Given the url for either the House or Senate Representatives page, scrapes
    basic info about each rep such as name, committees, district, and party.
    Also adds empty fields for counting number of bills sponsored by topic.
    Inputs:
        url - (str) for the chamber webpage
        chamber - (str) either 'House' or 'Senate'
        rep_info - dictionary of representative information.  This is modified
                   in place by the function.
    Outputs:
        None - modifies rep_info dictionary in place
    '''
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
