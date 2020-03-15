import sqlite3
import os


# Use this filename for the database
DATA_DIR = os.path.dirname(__file__)
DATABASE_FILENAME = os.path.join(DATA_DIR, './IssuetoImpact.db')


def get_rep_info(rep_name):
    '''
    Takes in rep name and returns information about them from the database

    Inputs:
        rep_name (str)

    Outputs:
        rep_info (tuple)
    '''

    if not rep_name:
        return None

    conn = sqlite3.connect(DATABASE_FILENAME)
    c = conn.cursor()

    query = 'SELECT * FROM reps WHERE reps.name = ?'
    arg = (rep_name,)
    r = c.execute(query, arg)

    results = r.fetchall()
    header = get_header(c)

    conn.close()

    return results



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
