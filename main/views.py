from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib import messages
import os

# from ratelimit.decorators import ratelimit
from snakefront.argparser import SnakefaceParser
from snakefront.settings import cfg
from main.models import Workflow
from main.forms import WorkflowForm
from main.tasks import run_workflow, serialize_workflow_statuses, run_get_source, serialize_runworkflow_job
from accounts.decorators import login_is_required
from snakefront.settings import (
    VIEW_RATE_LIMIT as rl_rate,
    VIEW_RATE_LIMIT_BLOCK as rl_block,
)
import json, time, re
from project.models  import Project
from main.utils import get_snakefile_choices
from api.models import RunWorkflow, RunWorkflowJob, RunWorkflowMessage
from s3browser import views as s3views


def parseConfig(command):
    command = "snakemake --snakefile /Users/mhb8436/Workspaces/snake/projects/88bd48fe-9d9d-4b9d-ba9d-7ec0885018f6/74/workflow/Snakefile --cores 1 --wms-monitor http://127.0.0.1:8000"
    command_arr = command.split(' ')
    new_command_arr = []
    config_arr = []
    config_ck = len(command_arr)
    next_config_ck = len(command_arr)
    for i, value in enumerate(command_arr):
        if '--config' == value:
            config_ck = i
        if i > config_ck and '--' in value:
            next_config_ck = i
            break
    print('parseConfig' , command_arr, config_ck, next_config_ck)
    if config_ck < len(command_arr):
        new_command_arr = command_arr[0:config_ck-1] + command_arr[next_config_ck:]
        config_arr = command_arr[config_ck:next_config_ck]
    else:
        new_command_arr = command_arr
    print('parseConfig' , new_command_arr, config_arr)

@login_is_required
#@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def index(request):
    parseConfig('')
    workflows = []
    projects = []
    if request.user.is_authenticated:
        # workflows = Workflow.objects.filter(owners=request.user)
        workflows = Workflow.objects.all().order_by('-add_date')[:5]
        projects = Project.objects.all().order_by('-created_at')[:5]
    print('index', projects, workflows)
    return render(
        request,
        "main/dashboard.html",
        {"workflows": workflows, "projects":projects,"page_title": "Dashboard"},
    )


# Workflows
@login_is_required
#@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def project_workflows(request, project_id):
    workflows = None
    project = None
    if request.user.is_authenticated:
        project = Project.objects.get(pk=project_id)
        workflows = Workflow.objects.filter(project=project)
    return render(
        request,
        "main/index.html",        
        {"workflows":workflows, "page_title": "%s Project Workflows"%(project.name), "project":project}
    )

@login_is_required
#@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def delete_workflow(request, wid):
    
    workflow = get_object_or_404(Workflow, pk=wid)
    project = Project.objects.get(pk=workflow.project.uuid)
    # Ensure that the user is an owner
    print('delete_workflow', project, workflow.owners.all(), request.user)
    # if request.user not in workflow.owners.all():
    #     return HttpResponseForbidden()
    workflow.delete()
    return redirect("main:project_workflows", project_id=project.uuid)


@login_is_required
#@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def cancel_workflow(request, wid):
    workflow = get_object_or_404(Workflow, pk=wid)

    # Ensure that the user is an owner
    # if request.user not in workflow.owners.all():
    #     return HttpResponseForbidden()
    workflow.status = "CANCELLED"
    workflow.save()
    messages.info(
        request, "Your workflow has been cancelled, and will stop within 10 seconds."
    )
    return redirect("main:view_workflow", wid=workflow.id)


@login_is_required
#@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def edit_workflow(request, wid):

    workflow = get_object_or_404(Workflow, pk=wid)

    # Ensure that the user is an owner
    if request.user not in workflow.owners.all():
        return HttpResponseForbidden()

    # Give a warning if the snakefile doesn't exist
    if not os.path.exists(workflow.snakefile):
        messages.warning(
            request, "Warning: This snakefile doesn't appear to exist anymore."
        )

    # Create and update a parser with the current settings
    parser = SnakefaceParser()
    parser.load(workflow.data)
    return edit_or_update_workflow(request, workflow=workflow, parser=parser)


@login_is_required
#@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def new_workflow(request):
    parser = SnakefaceParser()
    if request.user.is_authenticated:
        return edit_or_update_workflow(request, parser=parser)
    return HttpResponseForbidden()

@login_is_required
#@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def new_project_workflow(request, project_id):
    parser = SnakefaceParser()
    if request.user.is_authenticated:
        project = Project.objects.get(pk=project_id)
        return edit_or_update_workflow(request, parser=parser, project=project)
    return HttpResponseForbidden()

@login_is_required
#@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def new_project_workflow1(request, project_id):
    projects = Project.objects.all()
    selected_project = Project.objects.get(pk=project_id)

    wtypes = [
        {'name': 'RNASEQ', 'value':'RNASEQ'},
        {'name': 'ML', 'value':'ML'},
    ]

    if request.method == "POST":
        for arg, setting in request.POST.items():
            print('new1', arg, setting)
        # create workflow model
        name = request.POST.get('name')
        project_id = request.POST.get('project')
        project = Project.objects.get(pk=project_id)
        git_address = request.POST.get('git_address')
        git_branch = request.POST.get('git_branch')
        git_tag = request.POST.get('git_tag')
        s3_prefix = request.POST.get('s3_prefix')
        workdir = os.path.join(*[cfg.WORKDIR, project_id, name])
        workflow = Workflow(name=name, project=project,git_address=git_address, git_tag=git_tag, git_branch=git_branch, workdir=workdir, s3_prefix=s3_prefix)
        workflow.save()
        s3views.create_workflow(selected_project.name, name)
        # execute snakedepoly 
        return run_get_source(request=request, wid=workflow.id)
        

    return render(
        request,
        "workflows/new1.html",
        {
            "wtypes": wtypes,
            "page_title": "New Workflow",
            "projects": projects,
            "selected_project": selected_project,
            "selected_wtype": {'name': 'RNASEQ', 'value':'RNASEQ'}
        },
    )

@login_is_required
#@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def new_or_edit_project_workflow2(request, project_id, wid):
    print('new_or_edit_project_workflow2')
    project = Project.objects.get(pk=project_id)
    workflow = Workflow.objects.get(pk=wid)
    
    if request.method == "POST":
        parser = SnakefaceParser()
        for arg, setting in request.POST.items():
            print('new2', arg, setting)
            parser.set(arg, setting)
        if (Workflow.objects.filter(owners=request.user).count() >= cfg.USER_WORKFLOW_LIMIT):
            messages.info(
                request, "You are at the workflow limit of %s" % cfg.USER_WORKFLOW_LIMIT
            )
        elif not parser.validate():
            messages.info(request, parser.errors)
        else:
            print('save workflow', parser.to_dict(), parser.snakefile)
            #save workflow
            workflow.data = parser.to_dict()
            workflow.snakefile = parser.snakefile            
            workflow.private = (
                True if cfg.PRIVATE_ONLY else request.POST.get("private", 1) == 1
            )
            workflow.owners.add(request.user)
            workflow.save()
            return redirect("main:project_workflows", project_id=project_id)
    
    
    snakefile_lst = []
    count = 0
    while True:
        workdir = os.path.join(*[cfg.WORKDIR, str(project.uuid), str(workflow.id)])
        snakefile_lst = get_snakefile_choices(workdir)
        if len(snakefile_lst) > 0:
            break
        count = count+1
        if count > 500000:
            break
    parser = SnakefaceParser(snakefile_lst)
    # parser.set_snakefiles([snakefile_lst[0][0]])
    snakefile_content = None
    # read snakefile    
    try:
        f = open(snakefile_lst[0][0])
        snakefile_content = f.read()
    except Exception as e:
        print(e)
        snakefile_content = None
    
    # if workflow edit 
    print('new_or_edit_project_workflow2', 'workflow.data', workflow.data, count)
    if workflow.data is not None:
        parser.load(workflow.data)

    if not snakefile_content:
        message = (
            "No Snakefiles were found in any path under %s."% (workdir)
        )
        messages.info(request, message)
        return redirect("main:view_workflow", wid=wid)

    print('parser', parser.groups) 
    return render(
        request,
        "workflows/new2.html",
        {
            "groups": parser.groups,
            "page_title": "Workflow %s Execution Argument Setting" %(workflow.name), 
            "project":project,
            "workflow": workflow,
            "snakefile_content": snakefile_content
        },
    )


def edit_or_update_workflow(request, parser, workflow=None, project=None):
    """A shared function to edit or update an existing workflow."""

    # Ensure the user has permission to update
    if workflow:
        existed = True
        action = "update"
        if request.user not in workflow.owners.all():
            return HttpResponseForbidden()
    else:
        workflow = Workflow()
        action = "create"
        existed = False

    form = WorkflowForm(request.POST or None, instance=workflow)

    # Case 1: parse a provided form to update current data
    if request.method == "POST" and form.is_valid():

        for arg, setting in request.POST.items():
            parser.set(arg, setting)

        # Has the user gone over the workflow number limit?
        if (
            Workflow.objects.filter(owners=request.user).count()
            >= cfg.USER_WORKFLOW_LIMIT
        ):
            messages.info(
                request, "You are at the workflow limit of %s" % cfg.USER_WORKFLOW_LIMIT
            )
        elif not parser.validate():
            messages.info(request, parser.errors)
        else:
            print("Creating new workflow")
            workflow = form.save()
            print("Creating new workflow2", workflow)
            workflow.data = parser.to_dict()
            workflow.snakefile = parser.snakefile
            workflow.workdir = request.POST.get("workdirs", cfg.WORKDIR)
            workflow.private = (
                True if cfg.PRIVATE_ONLY else request.POST.get("private", 1) == 1
            )
            workflow.owners.add(request.user)
            project_id = request.POST.get("project", "")
            project = Project.objects.get(pk=project_id)
            workflow.project = project
            # Save updates the dag and command
            # print("Creating new workflow3", workflow)
            workflow.save()
            # print('Created new workflow', workflow.id, workflow.command)
            return run_workflow(request=request, wid=workflow.id, uid=request.user.id)

    # Case 2: no snakefiles:
    if not parser.snakefiles:
        message = (
            "No Snakefiles were found in any path under %s."
            " You must have one to %s a workflow." % (cfg.WORKDIR, action)
        )
        messages.info(request, message)
        return redirect("main:dashboard")

    # Case 3: Render an empty form with current working directory
    if existed:
        form.fields["workdirs"].initial = workflow.workdir
    # print("Creating new workflow", "parser", parser.groups)
    projects = Project.objects.all()
    return render(
        request,
        "workflows/new.html",
        {
            "groups": parser.groups,
            "page_title": "%s Workflow" % action.capitalize(),
            "form": form,
            "workflow_id": getattr(workflow, "id", None),
            "projects": projects,
            "selected_project": project,
        },
    )


@login_is_required
#@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def workflow_command(request):
    """is called from the browser via POST to update the command"""
    parser = SnakefaceParser()
    if request.method == "POST":
        for arg, setting in request.POST.items():
            parser.set(arg, setting)
        return JsonResponse({"command": parser.command})


@login_is_required
def workflow_statuses(request, wid):
    """return serialized workflow statuses for the details view."""
    workflow = get_object_or_404(Workflow, pk=wid)
    return JsonResponse({"data": serialize_workflow_statuses(workflow)})


@login_is_required
#@ratelimit(key="ip", rate=rl_rate, block=rl_block)
def view_workflow(request, wid):
    workflow = get_object_or_404(Workflow, pk=wid)
    print('view_workflow', workflow.project.uuid)
    project = get_object_or_404(Project, pk=workflow.project.uuid)
    
    runworkflows = RunWorkflow.objects.filter(workflow=workflow, task=None)
    data = []
    for rw in runworkflows:
        data.append({
            'id': rw.id,
            'name': rw.name,
            'status': rw.status,
            'done': rw.done if rw.done else '',
            'total': rw.total if rw.total else '',
            'started_at': rw.started_at.strftime("%Y%m%d %H%M%S"),
            'completed_at': rw.started_at.strftime("%Y%m%d %H%M%S"),
            'worflow_id': rw.workflow_id,
            'task_id': rw.task_id,
        })
    return render(
        request,
        "workflows/detail.html",
        {
            "project":project,
            "workflow": workflow,
            "runworkflows": data,
            "page_title": "%s: %s" % (workflow.name or "Workflow", workflow.id),
        },
    )


def view_workflow_report(request, wid):
    """If a workflow generated a report and the report exists, render it to a page"""
    workflow = get_object_or_404(Workflow, pk=wid)
    report = workflow.get_report()
    if not report:
        messages.info(request, "This workflow does not have a report file.")
        redirect("main:view_workflow", wid=workflow.id)
    return render(
        request,
        "workflows/report.html",
        {"workflow": workflow, "page_title": "Report", "report": report},
    )

# @login_is_required
# def view_runworkflow(request, rwid):
#     run_workflow = RunWorkflow.objects.get(pk=rwid)
#     run_workflow_jobs = RunWorkflowJob.objects.filter(run_workflow=run_workflow)
#     return render(
#         request,
#         "workflows/run_workflow_jobs.html",
#         {
#             "runworkflowjobs": run_workflow_jobs,
#             "page_title":  "%s: %s" % (run_workflow.name, "Workflow Jobs"),
#         }
#     )

@login_is_required
def runworkflow_jobs(request, rwfid):

    run_workflow = RunWorkflow.objects.get(pk=rwfid)
    run_workflow_jobs = RunWorkflowJob.objects.filter(run_workflow=rwfid)
    run_workflow_status = RunWorkflowMessage.objects.filter(run_workflow=rwfid)
    data = []
    for job in run_workflow_jobs:
        data.append({
            'jobid': job.jobid,
            'run_workflow_id': job.run_workflow,
            'msg': job.msg,
            'status': job.status,
            'reason': job.reason,
            'name': job.name,
            'input': job.input,
            'output': job.output,
            'log': job.log,
            'wildcards': job.wildcards,
            'is_checkpoint': job.is_checkpoint,
            'started_at': job.started_at.strftime('%Y%m%d %H%M%S'),
            'completed_at': job.completed_at.strftime('%Y%m%d %H%M%S'),
            'timestamp': job.timestamp,
        })
    
    for status in run_workflow_status:
        data.append({
            'jobid': '',
            'run_workflow_id': status.run_workflow,
            'msg': status.msg if status.msg else '',
            'status': status.status if status.status else '',
            'reason': status.msg if status.msg else '',
            'name': '',
            'input': '',
            'output': '',
            'log': '',
            'wildcards': '',
            'is_checkpoint': '',
            'started_at': status.timestamp.strftime('%Y%m%d %H%M%S'),
            'completed_at': status.timestamp.strftime('%Y%m%d %H%M%S'),
            'timestamp': status.timestamp,

        })
    
    data2 = []
    
    for item in data:
        if item['reason'] and re.search("traceback|exception", item['reason'], re.IGNORECASE):
            item['status'] =  "error"
        else:
            item['status'] =  "success"
        data2.append(item)
    data2.sort(key=lambda x: x['timestamp'])

    return render(
        request,
        "workflows/run_workflow_jobs.html",
        {
            "runworkflowjobs": data2,
            "page_title":  "%s: %s" % (run_workflow.name, "Workflow Jobs"),
        }
    )