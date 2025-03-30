from django.conf import settings

from rest_framework.renderers import JSONRenderer
# from ratelimit.mixins import RatelimitMixin
from django.shortcuts import get_object_or_404

from main.models import Workflow, WorkflowStatus
from django_celery_beat.models import PeriodicTask, PeriodicTasks, CrontabSchedule, IntervalSchedule

from api.models import RunWorkflow, RunWorkflowJob
from snakefront.settings import cfg
from rest_framework.response import Response
from rest_framework.views import APIView
from .permissions import check_user_authentication

import json
import traceback
import uuid 
from api.utils import maintain_job, upload_folder

class ServiceInfo(APIView):
    
    def get(self, request):
        print('GET /api/service-info')
        return Response({'status':'running'})



class CreateWorkflow(APIView):

    def get(self, request):
        print('GET /create_workflow', request.GET.items())
        for arg, setting in request.GET.items():
            print('GET /create_workflow', arg, setting)
        # workflow_id = request.META['HTTP_AUTHORIZATION']
        # print(request.headers)
        # workflow_id = request.headers.get('Authorization')
        # workflow_id = workflow_id.replace('Bearer ','')
        workflow_id = request.GET.get('workflow_id')
        task_id = request.GET.get('task_id')
        task = None
        if task_id:
            task = PeriodicTask.objects.get(pk=task_id)
        try:        
            workflow = Workflow.objects.filter(id=workflow_id).first()
            print('GET /create_workflow','workflow', workflow_id, workflow)
            run_workflow = RunWorkflow.objects.create(
                name = str(uuid.uuid4()),
                status = "Running",
                workflow = workflow,
                task = task
            )
            run_workflow.save()
            return Response(status=200, data=run_workflow.get_workflow())
        except:
            traceback.print_exc()
            return Response(status=500, data={'msg':'error'})


class UpdateWorkflow(APIView):
    
    def post(self, request):
        print('POST /update_workflow_status')
        errors = None
        try:
            # print('update_workflow_status 1', request.data.get('msg'))
            msg = request.data.get('msg')
            timestamp = request.data.get('timestamp')
            id = request.data.get('id')
            # print('/update_workflow_status 2', msg, id)
        except:
            traceback.print_exc()
            errors = {'msg':'error'}
        if errors:
            return Response(status=500, data=errors)
        # if isinstance(msg, dict):
        maintain_job(msg=msg, wf_id=id)
        return Response(status=200, data={'msg':'ok'})


class UploadFolder(APIView):

    def post(self, request):
        print('POST /upload_folder')
        errors = None
        try:
            project_name = request.data.get('project_name')
            workflow_name = request.data.get('workflow_name')
            folder = request.data.get('folder')
        except:
            traceback.print_exc()
            errors = {'msg':'error'}
        if errors:
            return Response(status=500, data=errors)
        try:
            upload_folder(project_name=project_name, workflow_name=workflow_name, folder=folder)
        except:
            pass
        return Response(status=200, data={'msg':'ok'})


# class ServiceInfo(RatelimitMixin, APIView):
#     """Return a 200 response to indicate a running service. Note that we are
#     not currently including all required fields. See:
#     https://ga4gh.github.io/workflow-execution-service-schemas/docs/#operation/GetServiceInfo
#     """

#     ratelimit_key = "ip"
#     ratelimit_rate = settings.VIEW_RATE_LIMIT
#     ratelimit_block = settings.VIEW_RATE_LIMIT_BLOCK
#     ratelimit_method = "GET"
#     renderer_classes = (JSONRenderer,)

#     def get(self, request):
#         print("GET /service-info")

#         data = {
#             "id": "snakefront",
#             "status": "running",  # Extra field looked for by Snakemake
#             "name": "Snakemake Workflow Interface",
#             "type": {"group": "org.ga4gh", "artifact": "beacon", "version": "1.0.0"},
#             "description": "This service provides an interface to interact with Snakemake.",
#             "organization": {"name": "Snakemake", "url": ""},
#             "contactUrl": cfg.HELP_CONTACT_URL,
#             "documentationUrl": "",
#             "createdAt": "2020-12-04T12:57:19Z",
#             "updatedAt": cfg.UPDATED_AT,
#             "environment": cfg.ENVIRONMENT,
#             "version": "0.1",
#             "auth_instructions_url": "",
#         }

#         # Must make model json serializable
#         return Response(status=200, data=data)


# class CreateWorkflow(RatelimitMixin, APIView):
#     """Create a snakemake workflow. Given that we provide an API token, we
#     expect the workflow model to already be created and simply generate a run
#     for it.
#     """

#     ratelimit_key = "ip"
#     ratelimit_rate = settings.VIEW_RATE_LIMIT
#     ratelimit_block = settings.VIEW_RATE_LIMIT_BLOCK
#     ratelimit_method = "GET"
#     renderer_classes = (JSONRenderer,)

#     def get(self, request):
#         print("GET /create_workflow")

#         # If the request provides an id, check for workflow
#         workflow = request.GET.get("id")
#         user = None

#         if workflow:
#             workflow = get_object_or_404(Workflow, pk=workflow)

#         # Does the server require authentication?
#         if cfg.REQUIRE_AUTH:
#             user, response_code = check_user_authentication(request)
#             if not user:
#                 return Response(status=response_code)

#             # If we have a workflow, check that user has permission to use/update
#             if workflow and user not in workflow.owners.all():
#                 return Response(status=403)

#         # If we don't have a workflow, create one
#         if workflow:

#             # Remove old statuses here
#             workflow.workflowstatus_set.all().delete()

#         else:
#             # Add additional metadata to creation
#             snakefile = request.POST.get("snakefile")
#             workdir = request.POST.get("workdir")
#             command = request.POST.get("command")
#             workflow = Workflow(snakefile=snakefile, workdir=workdir, command=command)
#             workflow.save()
#             if user:
#                 workflow.owners.add(user)

#         data = {"id": workflow.id}
#         return Response(status=200, data=data)


# class UpdateWorkflow(RatelimitMixin, APIView):
#     """Update an existing snakemake workflow. Authentication is required,
#     and the workflow must exist.
#     """

#     ratelimit_key = "ip"
#     ratelimit_rate = settings.VIEW_RATE_LIMIT
#     ratelimit_block = settings.VIEW_RATE_LIMIT_BLOCK
#     ratelimit_method = "POST"
#     renderer_classes = (JSONRenderer,)

#     def post(self, request):
#         print("POST /update_workflow_status")

#         # We must have an existing workflow to update
#         workflow = get_object_or_404(Workflow, pk=request.POST.get("id"))

#         # Does the server require authentication?
#         if cfg.REQUIRE_AUTH:
#             user, response_code = check_user_authentication(request)
#             if not user:
#                 return Response(response_code)

#             # If we have a workflow, check that user has permission to use/update
#             if workflow and user not in workflow.owners.all():
#                 return Response(403)

#         # The message should be json dump of attributes
#         message = json.loads(request.POST.get("msg", {}))

#         # Update the workflow with a new status message
#         WorkflowStatus.objects.create(workflow=workflow, msg=message)
#         return Response(status=200, data={})
