from snakefront.settings import cfg
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from main.models import Workflow
from project.models import Project 
# from users.models import User
from accounts.models import CustomUser
from main.utils import CommandRunner, ThreadRunner
import os
import re
from api.models import RunWorkflow, RunWorkflowJob

# Notebook run workflow functions

def run_get_source(request, wid):
    """Thread run for get source from git"""
    workflow = get_object_or_404(Workflow, pk=wid)
    project = get_object_or_404(Project, uuid=workflow.project.uuid)
    t = ThreadRunner(target=doGetSource, args=[workflow.id])
    t.setDaemon(True)
    t.start()
    print('run_get_source thread id', t.thread_id)
    messages.success(request, "Workflow[%s] Source deploying from %s " % (workflow.id, workflow.git_address))
    return redirect("main:new_or_edit_project_workflow2", project_id=project.uuid, wid=workflow.id)

def run_scheduled_workflow(wid, tid, out_dir=None, data_dir=None, odate=None):    
    
    workflow = get_object_or_404(Workflow, pk=wid)    
    uid = 1
    if workflow.status == "RUNNING":
        print("This workflow[%s] is already running."%wid)

    else: # run_is_allowed(request) and running_notebook:
        workflow.reset()
        t = ThreadRunner(target=doRun, args=[workflow.id, uid, out_dir, tid, data_dir, odate])
        t.setDaemon(True)
        t.set_workflow(workflow)        
        t.start()
        print('run_workflow thread id', t.thread_id)
        workflow.thread = t.thread_id
        workflow.save()        
    return True



def run_workflow(request, wid, uid):
    """Top level function to ensure that the user has permission to do the run,
    and we direct to the correct function (notebook or not written, another backend)
    """
    # out_dir = None
    # data_dir = None
    out_dir = request.POST.get('out_dir', '')
    data_dir = request.POST.get('data_dir', '')
    odate = request.POST.get('odate', '')
    if len(out_dir) < 1:
        out_dir = None
    if len(data_dir) < 1:
        data_dir = None
    if len(odate) < 1:
        odate = None

    workflow = get_object_or_404(Workflow, pk=wid)
    user = get_object_or_404(CustomUser, pk=uid)
    running_notebook = cfg.NOTEBOOK or cfg.NOTEBOOK_ONLY
    # print('run_workflow', workflow.id, workflow.command, str(run_is_allowed(request)), str(running_notebook))
    # Ensure the user has permission to run the workflow
    if user not in workflow.members:
        messages.info(request, "You are not allowed to run this workflow.")

    # The workflow cannot already be running
    elif workflow.status == "RUNNING":
        messages.info(request, "This workflow is already running.")

    else: # run_is_allowed(request) and running_notebook:
        workflow.reset()
        t = ThreadRunner(target=doRun, args=[workflow.id, user.id, out_dir, None, data_dir, odate])
        t.setDaemon(True)
        t.set_workflow(workflow)        
        t.start()
        print('run_workflow thread id', t.thread_id)
        workflow.thread = t.thread_id
        workflow.save()
        messages.success(request, "Workflow %s has started running." % workflow.id)
    # else:
    #     messages.info(request, "Snakeface currently only supports notebook runs.")
    return redirect("main:view_workflow", wid=workflow.id)


# Permissions


def run_is_allowed(request):
    """Given a request, check that the run is allowed meaning:
    1. If running a notebook, we aren't over quota for jobs
    2. If not running a notebook, we aren't over user or global limits
    """
    running_notebook = cfg.NOTEBOOK or cfg.NOTEBOOK_ONLY
    running_jobs = Workflow.objects.filter(status="RUNNING").count()
    allowed = True
    if (
        running_notebook
        and cfg.MAXIMUM_NOTEBOOK_JOBS
        and running_jobs >= cfg.MAXIMUM_NOTEBOOK_JOBS
    ):
        messages.info(
            request,
            "You already have the maximum %s jobs running." % cfg.MAXIMUM_NOTEBOOK_JOBS,
        )
        allowed = False

    elif (
        not running_notebook
        and cfg.USER_WORKFLOW_RUNS_LIMIT
        >= Workflow.objects.filter(user=request.user, status="RUNNING").count()
    ):
        messages.info(
            request,
            "You are at your workflow active runs limit. Finish some and try again later.",
        )
        allowed = False

    elif not running_notebook and cfg.USER_WORKFLOW_GLOBAL_RUNS_LIMIT >= running_jobs:
        messages.info(
            request,
            "The server is at the global limit of workflow runs. Try again later.",
        )
        allowed = False

    return allowed


# run workflows

def serialize_runworkflow_statuses(workflow):
    """A shared helper function to serialize a list of run workflow statuses into
    json.
    """
    runworkflows = RunWorkflow.objects.filter(workflow=workflow, task=None)
    data = []
    for i, rw in enumerate(runworkflows):
        data.append({
            'id': rw.id,
            'name': rw.name,
            'status': rw.status,
            'done': rw.done,
            'total': rw.total,
            'started_at': rw.started_at.strftime("%Y%m%d %H%M%S"),
            'completed_at': rw.completed_at.strftime("%Y%m%d %H%M%S"),
            'worflow_id': rw.workflow_id,
            'task_id': rw.task_id,
        })
    return data
    
# Statuses

def serialize_workflow_statuses(workflow):
    """A shared helper function to serialize a list of workflow statuses into
    json.
    """
    levels = {
        "debug": "primary",
        "dag_debug": "primary",
        "info": "info",
        "warning": "warning",
        "error": "danger",
    }
    data = []
    for i, status in enumerate(workflow.workflowstatus_set.all()):
        entry = status.msg
        msg = entry.get("msg", "")
        level = levels.get(entry.get("level"), "secondary")
        badge = "<span class='badge badge-%s'>%s</span>" % (
            level,
            entry.get("level", "info"),
        )

        # If it's a traceback, format as code
        if msg and re.search("traceback|exception", msg, re.IGNORECASE):
            msg = "<code>%s</code>" % msg.replace("\n", "<br>")

        entry.update(
            {
                "order": i,
                "job": entry.get("job", ""),
                "msg": msg,
                "level": badge,
            }
        )
        data.append(entry)
    return data


def serialize_runworkflow_job(jobs):
    data = []
    for i, job in enumerate(jobs):
        entry = {
            'jobid': job.jobid,
            'msg': job.msg,
            'name': job.name,
            'input': job.input,
            'output': job.output,
            'log': job.log,
            'wildcards': job.wildcards,
            'is_checkpoint': job.is_checkpoint,
            'shell_command': job.shell_command,
            'status': job.status,
            'started_at': job.started_at,
            'completed_at': job.completed_at,
        }
        data.append(entry)
    return data

def doRun(wid, uid, out_dir=None, tid=None, data_dir=None, odate=None):
    """The task to run a workflow"""
    workflow = Workflow.objects.get(pk=wid)
    # user = CustomUser.objects.get(pk=uid)

    runner = CommandRunner()
    workflow.status = "RUNNING"
    workflow.save()
    command = workflow.command
    command_arr, config_arr = parseConfig(command)    
    command = ' '.join(command_arr) 

    if out_dir:
        config_arr.append('outputs_dir=%s'%(out_dir))        
    if data_dir:
        config_arr.append('data_dir=%s'%(data_dir))
    if odate:
        config_arr.append('odate=%s'%(odate))

    if len(config_arr) > 0:
        command = command + ' ' + ' '.join(config_arr)

    if tid:
        command = command + " --wms-monitor-arg task_id=%s workflow_id=%s" % (tid, wid)
    else:
        command = command + " --wms-monitor-arg workflow_id=%s" % wid
    # Define the function to determine cancelling the run
    cwd = os.path.dirname(workflow.snakefile)
    if cwd.split('/')[-1] == 'workflow':
        wdir = cwd.split('/')
        wdir.pop()
        cwd = str(os.sep).join(wdir)

    def cancel_workflow(wid):
        workflow = Workflow.objects.get(pk=wid)
        return workflow.status == "CANCELLED"
    # print('doRun', command, user.notebook_token)
    # if command.split(' ')[0] == 'snakemake':
    #     command = '/home/ubuntu/.local/share/virtualenvs/snake-T4jE69Ni/bin/' + command
    # Run the command, update when finished
    print('doRun',out_dir, data_dir,odate, command)
    runner.run_command(
        # workflow.command.split(" "),
        command.split(" "),
        env={"WMS_MONITOR_TOKEN": str(workflow.uuid)},
        cwd=cwd,
        cancel_func=cancel_workflow,
        cancel_func_kwargs={"wid": wid},
    )
    workflow.error = "<br>".join(runner.error)
    workflow.output = "<br>".join(runner.output)
    workflow.status = "NOTRUNNING"
    workflow.retval = runner.retval
    print('doRun','end', workflow.error, workflow.output, workflow.status, workflow.retval)
    workflow.save()



def doGetSource(wid):
    """ get Snakeflie and etc file from git address and tag using snakedeploy """
    workflow = Workflow.objects.get(pk=wid)
    project = Project.objects.get(pk=workflow.project.uuid)
    runner = CommandRunner()

    def cancel_deploy(wid):
        workflow = Workflow.objects.get(pk=wid)
        return False
        
    saved_directory = os.path.join(*[cfg.WORKDIR, str(project.uuid), str(workflow.id)])
    print('doGetSource', 'saved_directory', saved_directory, workflow.git_branch, workflow.git_tag)
    if not os.path.exists(saved_directory):
        os.makedirs(saved_directory)
        
    # command = "snakedeploy deploy-workflow %s %s --tag %s"%(workflow.git_address, saved_directory, workflow.git_tag)
    command = "snakedeploy deploy-workflow %s %s" % (workflow.git_address, saved_directory)
    if len(workflow.git_branch) > 0:
        command = command + ' --branch %s'%(workflow.git_branch)

    if len(workflow.git_tag) > 0:
        command = command + ' --tag %s'%(workflow.git_tag)

    print('doGetSource', 'command', command)
    runner.run_command(
        command.split(" "),
        env={'aa':'aa'},
        cancel_func=cancel_deploy,
        cancel_func_kwargs={"wid": wid},
    )
    error = runner.error
    output = runner.output
    retval = runner.retval
    print(error, output, retval)



def parseConfig(command):
    # command = "snakemake --snakefile /Users/mhb8436/Workspaces/snake/projects/88bd48fe-9d9d-4b9d-ba9d-7ec0885018f6/74/workflow/Snakefile --cores 1 --config name1=value1 name2=value2 --wms-monitor http://127.0.0.1:8000"
    command_arr = command.split(' ')
    config_arr = []
    config_ck = len(command_arr)
    next_config_ck = len(command_arr)
    for i, value in enumerate(command_arr):
        if '--config' == value:
            config_ck = i
        if i > config_ck and '--' in value:
            next_config_ck = i
            break    
    if config_ck < len(command_arr):
        new_command_arr = command_arr[0:config_ck-1] + command_arr[next_config_ck:]
        config_arr = command_arr[config_ck:next_config_ck]
    else:
        new_command_arr = command_arr
    config_arr = [value for value in config_arr if len(value) > 0]
    return new_command_arr, config_arr