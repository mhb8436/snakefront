from celery import shared_task, current_task
from celery import Celery
import time
import re
from main.models import Workflow, WorkflowStatus
from api.models import RunWorkflow, RunWorkflowJob, RunWorkflowMessage, RunWorkflowFolder
from django_celery_beat.models import PeriodicTask, PeriodicTasks, CrontabSchedule, IntervalSchedule
from main.tasks import run_scheduled_workflow
import datetime 
app = Celery('snakefront')

@shared_task
def task_snakemake_cmd(*args, **kwargs):
    print('task_snakemake_cmd', args, kwargs)
    if 'workflow_id' in kwargs and 'folder' in kwargs and 'task_id' in kwargs:
        print('run workflow')
        workflow_id = kwargs['workflow_id']
        folder = kwargs['folder']
        task_id = kwargs['task_id']
        odate = None
        if folder is None:
            print('dynamic folder from db ')
            workflow = Workflow.objects.get(pk=workflow_id)
            work_folder = RunWorkflowFolder.objects.filter(status='UPLOADED', workflow=workflow).first()
            if work_folder:
                folder = work_folder.folder_name
                work_folder.status = 'COMPLETE'
                work_folder.save()
        if 'odate_type' in kwargs and kwargs['odate_type'] == 'current':
            odate = datetime.datetime.now().strftime('%Y%m%d')
        print('task_snakemake_cmd','workflow_id folder task_id', workflow_id, folder, task_id, odate)
        run_scheduled_workflow(workflow_id, task_id, folder, odate)
        
    return True