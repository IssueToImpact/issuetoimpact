from django import forms

def _build_dropdown(options):
    """Convert a list to (value, caption) tuples."""
    return [(x, x) if x is not None else ('', NOPREF_STR) for x in options]

COMMITTEES = _build_dropdown(['Employment and Labor','Regulation',
'Education','Environment','Health','Transportation','Criminal Justice',
'Taxes','Energy and Public Utilities','Budget','Agriculture',
'Commerce and Economic Development','Human and Social Services',
'Veterans Affairs','Telecommunications and Information Technology'])

class SearchForm(forms.Form):
    query = forms.CharField(
        label='Search terms',
        help_text='e.g. energy',
        required=False)
    committee = forms.MultipleChoiceField(label='Committee Topics',
                                     choices=COMMITTEES,
                                     widget=forms.CheckboxSelectMultiple,
                                     required=False)

def rep(request):
    submitted = false
    if request.method == 'GET':
        form = SearchForm(request.GET)
        if form.is_valid():
            cd = form.cleaned_data
            return HttpResponseRedirect('/rep?submitted=True')
    else:
        form = SearchForm()
        if 'submitted' in request.GET:
            submitted = True

    return render_to_response(request, 'project_index.html', {'form': form, 'submitted': submitted})
