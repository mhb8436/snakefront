from django.contrib import admin

# Register your models here.
from .models import RunWorkflow, RunWorkflowFolder, RunWorkflowJob, RunWorkflowMessage

admin.site.register(RunWorkflow)
admin.site.register(RunWorkflowFolder)
admin.site.register(RunWorkflowJob)
admin.site.register(RunWorkflowMessage)