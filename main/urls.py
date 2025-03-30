
from django.urls import path
from . import views
from . import tasks

urlpatterns = [
    path("", views.index, name="dashboard"),
    path("proejct/<str:project_id>/workflows", views.project_workflows, name="project_workflows"),
    path("workflows/run/<int:wid>/<int:uid>", tasks.run_workflow, name="run_workflow"),
    path("workflows/new/", views.new_workflow, name="new_workflow"),
    path("workflows/new/<str:project_id>/", views.new_project_workflow, name="new_project_workflow"),
    path("workflows/new1/<str:project_id>/", views.new_project_workflow1, name="new_project_workflow1"),
    path("workflows/new2/<str:project_id>/<int:wid>", views.new_or_edit_project_workflow2, name="new_or_edit_project_workflow2"),
    path("workflows/<int:wid>/", views.view_workflow, name="view_workflow"),
    path("workflows/command/", views.workflow_command, name="workflow_command"),
    path(
        "workflows/<int:wid>/statuses/",
        views.workflow_statuses,
        name="workflow_statuses",
    ),
    path("workflows/<int:wid>/edit/", views.edit_workflow, name="edit_workflow"),
    path(
        "workflows/<int:wid>/report/",
        views.view_workflow_report,
        name="view_workflow_report",
    ),
    path("workflows/<int:wid>/delete/", views.delete_workflow, name="delete_workflow"),
    path("workflows/<int:wid>/cancel/", views.cancel_workflow, name="cancel_workflow"),

    path(
        "workflows/run/<int:rwfid>/jobs/",
        views.runworkflow_jobs,
        name="runworkflow_jobs",
    ),
]

app_name = "main"
