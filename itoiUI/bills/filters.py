from bills.models import Project
import django_filters

class ProjectFilter(django_filters.FilterSet):
    class Meta:
        model = Project
        fields = {
        'title': ['exact','contains'],
        'description': ['exact', 'contains']
        }
