from main.models import Workflow
from api.models import RunWorkflow, RunWorkflowJob, RunWorkflowMessage, RunWorkflowFolder
from project.models import Project
import os
import re
from snakefront.settings import cfg
import json
import traceback
import datetime

def maintain_job(msg, wf_id):
    run_workflow = RunWorkflow.objects.get(pk=wf_id)
    """
        The message should be a json dump
    """
    msg_json = {'level':''}
    print('maintain_job', msg)
    try:
        # print('maintain_job')
        msg_json = json.loads(msg)
        # print('maintain_job', msg_json)
    except Exception as e:
        # traceback.print_exc()
        # print('maintain_job 2', e, msg)
        msg_json = {'level':''}
    

    if "jobid" in msg_json.keys():
        if msg_json["level"] == 'job_info':            
            job = RunWorkflowJob.objects.create(
                level = msg_json['level'] if 'level' in msg_json else None,
                jobid = msg_json['jobid'] if 'jobid' in msg_json else None,
                run_workflow = run_workflow,
                msg = msg_json['msg'] if 'msg' in msg_json else None,
                reason = msg_json['reason'] if 'reason' in msg_json else None,
                name = msg_json['name'] if 'name' in msg_json else None,
                input = repr(msg_json['input']) if 'input' in msg_json else None,
                output = repr(msg_json['output']) if 'output' in msg_json else None,
                log = repr(msg_json['log']) if 'log' in msg_json else None,
                status = repr(msg_json['status']) if 'status' in msg_json else None,
                wildcards = repr(msg_json['wildcards']) if 'wildcards' in msg_json else None,
                is_checkpoint = msg_json['is_checkpoint'] if 'is_checkpoint' in msg_json else None,
                timestamp = datetime.datetime.fromtimestamp(msg_json['timestamp']) if 'timestamp' in msg_json else None,
            )
            job.save()
            return True
        if msg_json['level'] == 'job_finished':
            job = RunWorkflowJob.objects.filter(run_workflow=run_workflow, jobid=msg_json['jobid']).first()
            job.timestamp = datetime.datetime.fromtimestamp(msg_json['timestamp']) if 'timestamp' in msg_json else None
            job.job_done()
            return True
        
        if msg_json['level'] == 'job_error':
            job = RunWorkflowJob.objects.filter(run_workflow=run_workflow, jobid=msg_json['jobid']).first()
            job.timestamp = datetime.datetime.fromtimestamp(msg_json['timestamp']) if 'timestamp' in msg_json else None
            job.job_error()
            run_workflow.set_error()
            job.save()
            run_workflow.save()
    
    if msg_json['level'] == 'info':
        if msg_json['msg'] == 'Nothing to be done.':
            run_workflow.set_not_executed()
            run_workflow.save()
            return True
    
    if msg_json['level'] == 'progress':
        run_workflow.edit_workflow(msg_json['done'], msg_json['total'])
        run_workflow.save()
        return True
    
    if msg_json['level'] == 'error':
        run_workflow.set_error()
        run_workflow.save()
        return True
    
    if msg_json['level'] in ['shellcmd', 'info', 'debug','resources_info','run_info']:
        w_msg = RunWorkflowMessage.objects.create(
            msg = msg_json['msg'] if 'msg' in msg_json else None, 
            timestamp = datetime.datetime.fromtimestamp(msg_json['timestamp']) if 'timestamp' in msg_json else None,
            run_workflow=run_workflow, 
        )
        w_msg.save()
        return True
    
    return False



def upload_folder(project_name, workflow_name, folder):
    print('upload_folder', project_name, workflow_name, folder)
    project = Project.objects.filter(name=project_name).first()
    workflow = Workflow.objects.filter(name=workflow_name, project=project).first()
    uploaded_folder, created = RunWorkflowFolder.objects.get_or_create(
        workflow = workflow,
        folder_name = folder
    )
    print(uploaded_folder, created)
    uploaded_folder.save()
    return True
