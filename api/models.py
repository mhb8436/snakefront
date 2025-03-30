from django.db import models
from main.models import Workflow
from datetime import datetime
from snakefront.settings import cfg
# Create your models here.
from django.db.models.signals import post_save
from django.dispatch import receiver
import os
from django_celery_beat.models import PeriodicTask, PeriodicTasks, CrontabSchedule, IntervalSchedule


class RunWorkflow(models.Model):

    name = models.TextField("uuid4 name", unique=True)
    status = models.TextField("run status", blank=True, null=True)
    done = models.IntegerField("Job done count", blank=True, null=True)
    total = models.IntegerField("Job total count", blank=True, null=True)    
    started_at = models.DateTimeField("Workflow run start date", auto_now_add=True)
    completed_at = models.DateTimeField("Workflow run complete date", auto_now_add=True)
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, null=True, blank=True)
    task = models.ForeignKey(PeriodicTask, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return str(self.id) + '/' + self.name
    
    class Meta:
        app_label = "api"
    
    def set_error(self):
        self.status = 'Error'

    def edit_workflow(self, done, total):
        self.done = done
        self.total = total
        if done == total:
            self.status = 'Done'
            self.completed_at = datetime.now()
        
    def set_not_executed(self):
        self.done = 1
        self.status = 'No Execution'
    
    def get_workflow(self):
        return {
            "id": self.id,
            "name": self.name,
            "jobs_done": self.done,
            "jobs_total": self.total,
            "status": self.status,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
        }

# @receiver(post_save, sender=RunWorkflow)
# def create_run_workflow_directory(sender, instance, **kwargs):
#     print('post save callabck', instance)
#     workflow = instance.workflow
#     project = workflow.project
#     runworkflow_directory = os.path.join(*[cfg.WORKDIR, str(project.uuid), str(workflow.id), str(instance.id)])
#     if not os.path.exists(runworkflow_directory):
#         os.makedirs(runworkflow_directory)




class RunWorkflowMessage(models.Model):
    run_workflow = models.ForeignKey(RunWorkflow, on_delete=models.CASCADE, null=True, blank=True)
    msg = models.TextField("Message", null=True, blank=True)
    status = models.CharField("Message Status", max_length=30, null=True, blank=True)
    timestamp = models.DateTimeField("Snakemake TimeStamp", blank=True, null=True)

    def __str__(self):
        return str(self.id) + '/' + self.msg
    
    class Meta: 
        app_label = "api"
    
    def get_workflow_json(self):
        return {
            "id": self.id,
            "workflow": self.name,
            "date": self.date,
            "status": self.status,
            "timestamp": self.timestamp,
        }



class RunWorkflowJob(models.Model):
    level = models.CharField("Level", max_length=30, blank=True, null=True)
    jobid = models.IntegerField("Job ID", blank=True, null=True)
    run_workflow = models.ForeignKey(RunWorkflow, on_delete=models.CASCADE, null=True, blank=True)
    msg = models.TextField("Job Message", blank=True, null=True)
    reason = models.TextField("Job Message", blank=True, null=True)
    name = models.CharField("Job Name", max_length=30, blank=True, null=True)
    input = models.CharField("Input File", max_length=500, blank=True, null=True)
    output = models.CharField("Output File", max_length=500, blank=True, null=True)
    log = models.CharField("Log File", max_length=500, blank=True, null=True)
    wildcards = models.CharField("Wild Cards", max_length=100, blank=True, null=True)
    is_checkpoint = models.BooleanField("Check Point", blank=True, null=True)
    shell_command = models.CharField("Shell Command", max_length=300, blank=True, null=True)
    status = models.CharField("Status", max_length=30, blank=True, null=True)
    started_at = models.DateTimeField("Job run start date", auto_now_add=True)
    completed_at = models.DateTimeField("Job run complete date", auto_now_add=True)

    timestamp = models.DateTimeField("Snakemake TimeStamp", blank=True, null=True)


    def __str__(self):
        return str(id) + '/' + self.name
    

    def job_done(self):
        self.status = "Done"
        self.completed_at = datetime.now()
    
    def job_error(self):
        self.status = "Error"
        self.completed_at = datetime.now()
    
    def get_job_json(self):
        return {
            "jobid":self.jobid,
            "run_workflow_id": self.run_workflow,
            "msg": self.msg,
            "reason": self.reason,
            "name": self.name,
            "input": eval(self.input),
            "output": eval(self.output),
            "log": eval(self.log),
            "wildcards": eval(self.wildcards),
            "is_checkpoint": self.is_checkpoint,
            "shell_command": self.shell_command,
            "status": self.status,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "timestamp": self.timestamp,
        }

    class Meta:
        app_label = "api"

FOLDER_STATUS_CHOICES = [
    ("UPLOADED", "UPLOADED"),
    ("COMPLETE", "COMPLETE"),
    ("CANCELLED", "CANCELLED"),
]

class RunWorkflowFolder(models.Model):
    # s3_prefix = models.CharField("S3 Prefix for find workflow", max_length=1024, null=True, blank=True)
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, null=True, blank=True)
    folder_name = models.CharField("Output Folder", max_length=500, blank=True, null=True)
    status = models.CharField("Status", choices=FOLDER_STATUS_CHOICES, default="UPLOADED",  max_length=30, blank=True, null=True)
    uploaded_at = models.DateTimeField("Folder S3 Uploaded Date", auto_now_add=True)
    completed_at = models.DateTimeField("Folder Workflow Completed Date", auto_now_add=True)

    def __str__(self):
        return self.folder_name
    
    def folder_upload(self):
        self.status = FOLDER_STATUS_CHOICES[0]
        self.uploaded_at = datetime.now()
    
    def folder_complete(self):
        self.status = FOLDER_STATUS_CHOICES[1]
        self.completed_at = datetime.now()
    
    class Meta:
        app_label = "api"


