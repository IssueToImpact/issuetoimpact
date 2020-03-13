from django.urls import path
from bills import views

urlpatterns = [
    path("", views.project_index, name="project_index"),
    path("<int:pk>/", views.project_detail, name="project_detail"),
    url(r'^list$', views.project_list),
]
