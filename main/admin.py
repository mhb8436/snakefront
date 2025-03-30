from django.contrib import admin

# Register your models here.

from .models import Workflow, WorkflowStatus

admin.site.register(WorkflowStatus)
admin.site.register(Workflow)