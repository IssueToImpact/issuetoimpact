import traceback
import os
import sys
import requests
from geopy.geocoders import Nominatim
from functools import reduce
from operator import and_

from django.shortcuts import render
from django import forms

from filters import find_bills
from find_rep_contacts import find_rep_from_address
from get_rep_info import get_rep_info

##### BILL FILTERING AND RETURN ##########
NOPREF_STR = 'No preference'
COLUMN_NAMES = dict(
    bill_number='Bill Number',
    chamber='Chamber',
    status='Status',
    last_action_date='Last Action Date',
    topic='Topic',
    primary_sponsor='Primary Sponsor',
    bill_url='Bill URL',
    synopsis="Synopsis"
)


def _valid_result(res):
    """Validate results returned by find_courses."""
    (HEADER, RESULTS) = [0, 1]
    ok = (isinstance(res, (tuple, list)) and
          len(res) == 2 and
          isinstance(res[HEADER], (tuple, list)) and
          isinstance(res[RESULTS], (tuple, list)))
    if not ok:
        return False

    n = len(res[HEADER])

    def _valid_row(row):
        return isinstance(row, (tuple, list)) and len(row) == n
    return reduce(and_, (_valid_row(x) for x in res[RESULTS]), True)

def _build_dropdown(options):
    """Convert a list to (value, caption) tuples."""
    return [(x, x) if x is not None else ('', NOPREF_STR) for x in options]

TOPICS = _build_dropdown(['Employment and Labor','Regulation',
'Education','Environment','Health','Transportation','Criminal Justice',
'Taxes','Energy and Public Utilities','Budget','Agriculture',
'Commerce and Economic Development','Human and Social Services',
'Veterans Affairs','Telecommunications and Information Technology'])

class SearchForm(forms.Form):
    query = forms.CharField(
        label='Search terms',
        help_text='e.g. energy',
        required=False)
    topic = forms.MultipleChoiceField(label='Committee Topics',
                                     choices=TOPICS,
                                     widget=forms.CheckboxSelectMultiple,
                                     required=False)
    address = forms.CharField(
        label='Enter your address',
        help_text="""We're not storing it, just using it to find your
        representatives later on the page!""",
        required=False)

def home(request):
    context = {}
    res = None
    if request.method == 'GET':
        # create a form instance and populate it with data from the request:
        form = SearchForm(request.GET)
        # check whether it's valid:
        if form.is_valid():

            # Convert form data to an args dictionary for find_courses
            args = {}
            if form.cleaned_data['query']:
                args['terms'] = form.cleaned_data['query'].split()

            topic = form.cleaned_data['topic']
            if topic:
                args['topic'] = topic

            address = form.cleaned_data['address']

            topic_list = ['Agriculture','Budget','Commerce_and_Economic_Development',\
            'Criminal_Justice','Education','Energy_and_Public_Utilities',\
            'Environment','Health','Human_and_Social_Services',\
            'Employment_and_Labor','Public_Safety_and_Firearms','Regulation',\
            'Taxes','Telecommunications_and_Information_Technology',\
            'Transportation','Veterans_Affairs']

            if address:
                rep_dict = find_rep_from_address(address)
                if rep_dict:
                    for key in rep_dict.keys():
                        info = get_rep_info(key)
                        rep_dict[key]['info'] = list(info[0])
                        max = 0
                        max_ind = 0
                        for item, num in enumerate(rep_dict[key]['info']):
                            if item >= 5 and item <= 20:
                                if num > max:
                                    max = num
                                    max_ind = item - 5
                        max_topic = topic_list[max_ind]
                        rep_dict[key]['info'].append(max_topic)
                        rep_dict[key]['info'] = tuple(rep_dict[key]['info'])
            else:
                rep_dict = None
            try:
                res = find_bills(args)
            except Exception as e:
                print('Exception caught')
                print(e)
                bt = traceback.format_exception(*sys.exc_info()[:3])
                context['err'] = """
                An exception was thrown in find_bills:
                <pre>{}
{}</pre>
                """.format(e, '\n'.join(bt))

                res = None
    else:
        form = SearchForm()

    # Handle different responses of res
    if res is None:
        context['result'] = None
    elif isinstance(res, str):
        context['result'] = None
        context['err'] = res
        result = None
    elif not _valid_result(res):
        context['result'] = None
    else:
        columns, result = res


        colnames = [COLUMN_NAMES.get(col, col) for col in columns]
        context['rep_dict'] = rep_dict
        context['result'] = result
        context['num_results'] = len(result)
        context['columns'] = colnames


    context['form'] = form
    return render(request, 'index.html', context)
