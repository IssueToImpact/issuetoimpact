from django.shortcuts import render
from bills.models import Project

def project_index(request):
    projects = Project.objects.all()
    context = {
        'projects': projects
    }
    return render(request, 'project_index.html', context)

def project_detail(request, pk):
    project = Project.objects.get(pk=pk)
    context = {
        'project': project
    }
    return render(request, 'project_detail.html', context)

from bills.filters import ProjectFilter

def project_list(request):
	projects = Project.object.all()
	filter = ProjectFilter(request.GET, queryset = projects)
	return render(request, 'itoiUI/templates/project_index.html', {'filter' : filter})
