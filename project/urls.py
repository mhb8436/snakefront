
from django.urls import path
from . import views


urlpatterns = [
    path("projects", views.index, name="project_list"),
    path("project/new/", views.new_project, name="new_project"),
    path("project/<str:uuid>/", views.view_project, name="view_project"),
    path("project/<str:uuid>/edit/", views.edit_project, name="edit_project"),
    path("project/<str:uuid>/delete/", views.delete_project, name="delete_project"),
]

app_name = "project"
