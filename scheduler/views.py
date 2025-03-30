from django.shortcuts import render
from django_celery_beat.models import PeriodicTask, PeriodicTasks, CrontabSchedule, IntervalSchedule
from api.models import RunWorkflow, RunWorkflowJob

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib import messages
import os
from django.db.models import Count, Case, When, IntegerField
from snakefront.settings import cfg
from project.models import Project
from main.models import Workflow
import json
from accounts.decorators import login_is_required

@login_is_required
def index(request):
    print('scheduler index')
    ret_tasks = []
    workflow_dict = {}
    if request.user.is_authenticated:
        tasks = PeriodicTask.objects.all()
        workflows = Workflow.objects.all()
        for task in tasks:
            kwarg_dict = json.loads(task.kwargs)
            print(task.name, kwarg_dict)
            if 'workflow_id' in kwarg_dict:
                # workflow_dict[kwarg_dict['workflow_id']] = Workflow.objects.get(pk=kwarg_dict['workflow_id'])
                workflow = None
                try:
                    workflow = Workflow.objects.get(pk=kwarg_dict['workflow_id'])
                except:
                    pass
                scheduler = CrontabSchedule.objects.get(pk=task.crontab_id)
                ret_tasks.append({
                    'task': task, 'workflow':workflow, 'scheduler': scheduler
                })
            else:
                scheduler = CrontabSchedule.objects.get(pk=task.crontab_id)
                ret_tasks.append({
                    'task': task, 'workflow':None,  'scheduler': scheduler
                })

    return render(
        request,
        "scheduler/list.html",
        {"tasks":ret_tasks, "workflow": workflow_dict, "page_title":"Scheduler List"}
    )

FOLDER_TYPES = [
    {'id':'dynamic', 'name':'dynamic'},
    {'id':'fixed', 'name':'fixed'}
]

ODATE_TYPES = [
    {'id':'current', 'name':'current'},    
]

@login_is_required
def new_scheduler(request):
    projects = Project.objects.all()
    workflows = Workflow.objects.all()
    print('new_scheduler', 'workflows', workflows)
    if request.method == "POST":
        # for arg, setting in request.POST.items():
        #     print(arg, setting)
        print(request.POST['name'],request.POST['workflow'], request.POST['folder'],request.POST['schedule'],request.POST['folder_type'],request.POST['odate_type'],)
        # crontab  check 
        crontab = request.POST['schedule'].split(' ')
        crontab_id = None
        folder = request.POST['folder']
        if request.POST['folder_type'] == 'dyanmic':
            folder = None
        odate_type = None
        if request.POST['odate_type']:
            odate_type = request.POST['odate_type']
        crontab_obj = CrontabSchedule.objects.filter(minute=crontab[0], hour=crontab[1], day_of_week=crontab[2], day_of_month=crontab[3], month_of_year=crontab[4])
        if len(crontab_obj) > 0:
            print('exists_crontab', crontab_obj[0])
            crontab_id = crontab_obj[0].id
        else:
            crontab_obj = CrontabSchedule.objects.create(minute=crontab[0], hour=crontab[1], day_of_week=crontab[2], day_of_month=crontab[3], month_of_year=crontab[4])
            crontab_obj.save()
            crontab_id = crontab_obj.id
        print('crontab.id', crontab_id)
        task_obj = PeriodicTask.objects.create(
            name = request.POST['name'],
            task = "scheduler.tasks.task_snakemake_cmd",
            kwargs = json.dumps({'workflow_id': request.POST['workflow'], 'folder': folder}),
            description = request.POST['description'],
            crontab_id = crontab_id
        )
        task_obj.save()
        task_obj.kwargs = json.dumps({
            'workflow_id': request.POST['workflow'], 
            'folder': folder,
            'task_id':task_obj.id,
            'odate_type': odate_type,
        })
        task_obj.save()
        return redirect("scheduler:scheduler_list")

    return render(
        request,
        "scheduler/new.html",        
        {
            "projects": projects,
            "workflows": workflows,
            "selected_workflow": None,
            "folder_types": FOLDER_TYPES,
            "odate_types": ODATE_TYPES,
            "selected_folder_type": None,
            "schduler_id": None,
            "page_title": "New Scheduler"
        }
    )

@login_is_required
def edit_scheduler(request, task_id):
    print('edit_scheduler', task_id)
    workflows = Workflow.objects.all()
    task = PeriodicTask.objects.get(pk=task_id)
    if request.method == "POST":
        # print(request.POST['name'],request.POST['workflow'], request.POST['folder'],request.POST['schedule'],request.POST['folder_type'],request.POST['odate_type'], request.POST.get('enabled', "false"), )
        print(request.POST.keys())
        folder = request.POST['folder']
        if request.POST['folder_type'] == 'dynamic':
            folder = None
        odate_type = None
        if request.POST['odate_type']:
            selected_item = next((item for item in ODATE_TYPES if item['id'] == request.POST['odate_type']), False)
            print(selected_item)
            if selected_item:
                odate_type = selected_item['id']
        crontab = request.POST['schedule'].split(' ')
        crontab_id = None
        crontab_obj = CrontabSchedule.objects.filter(minute=crontab[0], hour=crontab[1], day_of_week=crontab[2], day_of_month=crontab[3], month_of_year=crontab[4])
        if len(crontab_obj) > 0:
            print('exists_crontab', crontab_obj[0])
            crontab_id = crontab_obj[0].id
        else:
            crontab_obj = CrontabSchedule.objects.create(minute=crontab[0], hour=crontab[1], day_of_week=crontab[2], day_of_month=crontab[3], month_of_year=crontab[4])
            crontab_obj.save()
            crontab_id = crontab_obj.id
        print('crontab.id', crontab_id)
        enabled = True
        task.name = request.POST['name']
        task.task = 'scheduler.tasks.task_snakemake_cmd'
        # task.kwargs = json.dumps({'workflow_id': request.POST['workflow'], 'folder': folder})
        task.description = request.POST['description']
        task.crontab_id = crontab_id
        task.enabled = True if 'enabled' in request.POST and request.POST['enabled'] == 'true' else False
        print('edit_scheduler', 'enabled', enabled)
        task.kwargs = json.dumps({
            'workflow_id': request.POST['workflow'], 
            'folder': folder,
            'task_id':task.id,
            'odate_type': odate_type,
        })        
        task.save()

        return redirect("scheduler:scheduler_list")

    selected_workflow = None
    selected_folder = None
    selected_folder_type = FOLDER_TYPES[0]
    selected_odate_type = None
    kwargs = json.loads(task.kwargs)
    if 'workflow_id' in kwargs:
        try:
            selected_workflow = Workflow.objects.get(pk=kwargs['workflow_id'])
        except:
            pass
    scheduler = None
    if task.crontab_id:
        scheduler = CrontabSchedule.objects.get(pk=task.crontab_id)
    if 'folder' in kwargs:
        selected_folder = kwargs['folder']
    if selected_folder:
        selected_folder_type = FOLDER_TYPES[1]
    if 'odate_type' in kwargs:
        selected_item = next((item for item in ODATE_TYPES if item['id'] == kwargs['odate_type']), False)
        if selected_item:
            selected_odate_type = selected_item
    
    print('edit_scheduler', task)    
    return render(
        request,
        "scheduler/edit.html", 
        {
            "task": task,
            "workflows": workflows,
            "selected_workflow": selected_workflow,
            "selected_folder": selected_folder,
            "folder_types": FOLDER_TYPES,
            "odate_types": ODATE_TYPES,
            "selected_folder_type": selected_folder_type,
            "selected_odate_type": selected_odate_type,
            "scheduler": scheduler,
            "page_title":  "Edit Scheduler [%s]" % (task.name)
        }
    )


@login_is_required
def delete_scheduler(request, task_id):
    print('delete_scheduler', task_id)
    instance = PeriodicTask.objects.get(pk=task_id)
    instance.delete()
    return redirect("scheduler:scheduler_list")


@login_is_required
def view_run_list(request, task_id):
    print('view_run_list')
    task = PeriodicTask.objects.get(pk=task_id)
    kwargs = json.loads(task.kwargs)
    workflow = None
    folder = None
    schedule = None
    if 'workflow_id' in kwargs:
        try:
            workflow = Workflow.objects.get(pk=kwargs['workflow_id'])
        except:
            pass
    if 'folder' in kwargs:
        folder = kwargs['folder']
    if task.crontab:
        schedule = CrontabSchedule.objects.get(pk=task.crontab.id)

    runworkflows = RunWorkflow.objects.filter(task=task)
    print('schedule', schedule)
    return render(
        request, 
        "scheduler/run_workflow_list.html",
        {
            "runworkflows": runworkflows,
            "task": task,
            "workflow": workflow,
            "folder": folder,
            "schedule": schedule,
            "page_title":  "Run Workflow List [%s]" % (task.name)
        }
    )

