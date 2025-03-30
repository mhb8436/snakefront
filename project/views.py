from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib import messages
import os
from django.db.models import Count, Case, When, IntegerField

# from ratelimit.decorators import ratelimit
from snakefront.argparser import SnakefaceParser
from snakefront.settings import cfg
from project.models import Project
from main.models import Workflow
from main.tasks import run_workflow, serialize_workflow_statuses
from accounts.decorators import login_is_required
from snakefront.settings import (
    VIEW_RATE_LIMIT as rl_rate,
    VIEW_RATE_LIMIT_BLOCK as rl_block,
)
import json
from .forms import ProjectForm
from s3browser import views as s3views

@login_is_required
# @ratelimit(key="ip", rate=rl_rate, block=rl_block)
def index(request):
    projects = None
    if request.user.is_authenticated:
        # projects = Project.objects.all()
        projects = Project.objects.annotate(
            num_notrunning=Count(Case(
                When(workflow__status='NOTRUNNING',then=1), output_field=IntegerField()
            ))
        ).annotate(
            num_running=Count(Case(
                When(workflow__status='RUNNING', then=1), output_field=IntegerField()
            ))
        )
    print('project index', projects)
    return render(
        request,
        "projects/list.html",
        {"projects":projects, "page_title":"Project List"}
    )

@login_is_required
# @ratelimit(key="ip", rate=rl_rate, block=rl_block)
def view_project(request, uuid):
    project = get_object_or_404(Project, pk=uuid)
    return render(
        request,
        "project/detail.html",
        {
            "project": project,
            "page_title": "%s: %s" % (project.name or "Project", project.uuid),
        }
    )

@login_is_required
# @ratelimit(key="ip", rate=rl_rate, block=rl_block)
def new_project(request):
    project = Project()
    form = ProjectForm(request.POST or None, instance=project)
    print("new_project", "method", request.method, form.is_valid())
    if request.method == "POST" and form.is_valid():        
        project = form.save()
        project.save()
        print('new_project', project)
        # create directory 
        directory = os.path.join(cfg.WORKDIR, str(project.uuid))
        try:
            os.makedirs(directory)
            s3views.create_project(project.name)
        except OSError as e:
            print(e)            
        return redirect("project:project_list")
    
    return render(
        request,
        "projects/new.html",        
        {
            "form": form,
            "page_title": "New Project"
        }
    )

@login_is_required
# @ratelimit(key="ip", rate=rl_rate, block=rl_block)
def edit_project(request, uuid):
    project = get_object_or_404(Project, pk=uuid)
    form = ProjectForm(request.POST or None, instance=project)
    if request.method == "POST" and form.is_valid():
        project = form.save()
        project.save()
        try:
            s3views.create_project(project.name)
        except Exception as e:
            print(e)
        print('new_project', project)
        return redirect("project:project_list")

    return render(
        request,
        "projects/edit.html",
        {
            "project": project,
            "form": form,
            "page_title": "%s: %s" % (project.name or "Project", project.uuid),
        }
    )

@login_is_required
def delete_project(request, uuid):
    project = get_object_or_404(Project, pk=uuid)
    project.delete()
    return redirect("project:project_list")