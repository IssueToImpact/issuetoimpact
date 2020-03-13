import traceback
import os
import sys
from functools import reduce
from operator import and_

from django.shortcuts import render
from django import forms

from filters import find_bills

# def project_index(request):
#     projects = Project.objects.all()
#     context = {
#         'projects': projects
#     }
#     return render(request, 'project_index.html', context)

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

            try:
                res = find_bills(args)
            except Exception as e:
                print('Exception caught')
                print(e)
                bt = traceback.format_exception(*sys.exc_info()[:3])
                context['err'] = """
                An exception was thrown in find_courses:
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
        context['err'] = ('Return of find_courses has the wrong data type. '
                          'Should be a tuple of length 4 with one string and '
                          'three lists.')
    else:
        columns, result = res

        # Wrap in tuple if result is not already
        if result and isinstance(result[0], str):
            result = [(r,) for r in result]

        context['result'] = result
        context['num_results'] = len(result)
        context['columns'] = [COLUMN_NAMES.get(col, col) for col in columns]

    context['form'] = form
    return render(request, 'index.html', context)
