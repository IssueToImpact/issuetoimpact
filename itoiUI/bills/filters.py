import sqlite3
import os


# Use this filename for the database
# DATA_DIR = ''
# DATABASE_FILENAME = os.path.join(DATA_DIR, 'IssuetoImpact.db')
DATA_DIR = os.path.dirname(__file__)
DATABASE_FILENAME = os.path.join(DATA_DIR, '../IssuetoImpact.db')



ARG_INFO = {'terms': {'table': 'bill_keywords'},
            'topic': {'table': 'bills'}}


def find_bills(args_from_ui):
    '''
    Takes a dictionary containing search criteria and returns courses
    that match the criteria.  The dictionary will contain some of the
    following fields:

      - topic is list of strings
           -> ["'MWF'", "'TR'", etc.]
      - terms is a list of strings string: ["quantum", "plato"]

    Returns a pair: an ordered list of attribute names and a list the
     containing query results.  Returns ([], []) when the dictionary
     is empty.
    '''
    assert_valid_input(args_from_ui)

    if not args_from_ui:
        return ([], [])

    conn = sqlite3.connect(DATABASE_FILENAME)
    c = conn.cursor()

    query, arg_tuple = generate_query(args_from_ui)
    print(query)
    query = 'FROM bill_keywords SELECT *'
    print(arg_tuple)
    r = c.execute(query, arg_tuple)
    results = r.fetchall()
    header = get_header(c)
    conn.close()

    return (header, results)


def generate_query(args_from_ui):
    '''
    Put all the query functions together to make the final text query to send

    Inputs: Arguments passed in from the UI (dictionary)

    Returns: A tuple: (string of query, tuple of arguments)
    '''
    args = args_from_ui.keys()
    vals = args_from_ui.values()

    select_cols = create_select(args)
    join_lst, on_lst = create_join(args)
    where_conds, query_args = generate_where_conditions(args_from_ui)

    query_string = 'SELECT ' + ', '.join(select_cols)\
                    + ' FROM bills ' \

    if join_lst:
        query_string += ' JOIN ' + ' JOIN '.join(join_lst) \
                     + ' ON ' + ' AND '.join(on_lst) \

    if where_conds:
        query_string += 'WHERE ' + ' AND '.join(where_conds)

    return (query_string, tuple(query_args))


def create_select(args_from_dict):
    '''
    Take in the processed arg names and use that to determine what outputs
    need to come out of the function according to the table in the write up

    Inputs: Keys from the dictionary of arguments
    Returns: Columns to select in the SQL query (list)
    '''
    select_cols = ['bill_number', 'chamber', 'status', 'last_action_date',\
    'topic', 'primary_sponsor', 'bill_url', 'synopsis']
    #'tweet_id', 'text',\
    #'date', 'user', 'url']

    return select_cols


def create_join(args_from_dict):
    '''
    Take in the arguments from the processed dictionary (the keys) and use them
    to create two lists that will be put together to create the join, where, and
    on portion of the SQL query.

    Inputs: Keys from the dictionary of arguments
    Returns: a tuple (list of strings for the join, list of text for the on)
    '''
    join_lst = []
    on_lst = []

    if 'terms' in args_from_dict:
        join_lst.extend(['bill_keywords'])
        on_lst.extend(['bills.bill_number = bill_keywords.bill_number'])

    #join_lst.append(['tweets'])
    #on_lst.append('bills.bill_num = tweets.bill_num')

    return (join_lst, on_lst)


def generate_where_conditions(args_from_ui):
    '''
    Take in arguments from the UI and generate the filters needed for the query

    Inputs: Arguments passed in from the UI (dictionary)

    Returns: a tuple (list of where conditions, list of arguments)
    '''
    where_conds = []
    query_args = []

    for arg, val in args_from_ui.items():
        if arg == 'terms':
            sq, qa = generate_terms_subquery(val)
            where_conds.append('bills.bill_number' + ' IN ' + sq)
            query_args.extend(qa)
        else:
            if type(val) == list:
                query_args.extend(val)
                where_conds.append(ARG_INFO[arg]['table'] + '.' + arg + \
                    ' IN ({})'.format(', '.join(['?'] * len(val))))
            else:
                query_args.append(val)
                where_conds.append(ARG_INFO[arg]['table'] + '.' \
                + arg + ARG_INFO[arg]['where_cond'])

    return (where_conds, query_args)


def generate_terms_subquery(val):
    '''
    Generate the subquery necessary to filter based on keywords

    Inputs: values from the args dictionary

    Outputs: a tuple (subquery string, list of arguments)
    '''
    query_args = val + [len(val)]

    query = ''' (SELECT bill_number \
    FROM (SELECT bill_keywords.bill_number, count(*) as num_words \
          FROM bill_keywords \
          WHERE bill_keywords.keyword in ({}) \
          GROUP BY bill_keywords.bill_number) \
    WHERE num_words = ?)'''.format(', '.join(['?']* len(val)))

    return (query, query_args)


########### auxiliary functions #################
########### do not change this code #############

def assert_valid_input(args_from_ui):
    '''
    Verify that the input conforms to the standards set in the
    assignment.
    '''

    assert isinstance(args_from_ui, dict)

    acceptable_keys = set(['terms', 'topic'])
    assert set(args_from_ui.keys()).issubset(acceptable_keys)

    # day is a list of strings, if it exists
    assert isinstance(args_from_ui.get("topic", []), (list, tuple))
    assert all([isinstance(s, str) for s in args_from_ui.get("topic", [])])

    # terms is a non-empty list of strings, if it exists
    terms = args_from_ui.get("terms", [""])
    assert terms
    assert isinstance(terms, (list, tuple))
    assert all([isinstance(s, str) for s in terms])

def get_header(cursor):
    '''
    Given a cursor object, returns the appropriate header (column names)
    '''
    header = []

    for i in cursor.description:
        s = i[0]
        if "." in s:
            s = s[s.find(".")+1:]
        header.append(s)

    return header
