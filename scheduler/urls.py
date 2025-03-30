from django.urls import path
from . import views

urlpatterns = [
    path("schedulers", views.index, name="scheduler_list"),
    path("scheduler/new/", views.new_scheduler, name="new_scheduler"),    
    path("scheduler/<str:task_id>/edit/", views.edit_scheduler, name="edit_scheduler"),
    path("scheduler/<str:task_id>/delete/", views.delete_scheduler, name="delete_scheduler"),
    path("scheduler/<str:task_id>/run/", views.view_run_list, name="view_run_list"),
]

app_name = "scheduler"
