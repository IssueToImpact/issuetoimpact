from django.urls import path
from bills import views
from bills import forms

urlpatterns = [
    path("", views.project_index, name="project_index"),
    path("<int:pk>/", views.project_detail, name="project_detail"),
    #path('', forms.forms, name='search'),
]
