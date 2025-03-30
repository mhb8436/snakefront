from django.conf.urls import url
from django.urls import path

from snakefront.settings import cfg
import api.views as api_views
from .permissions import AllowAnyGet

urlpatterns = [
    path(
        "api/service-info",
        api_views.ServiceInfo.as_view(),
        name="service_info",
    ),
    path(
        "create_workflow",
        api_views.CreateWorkflow.as_view(),
        name="create_workflow",
    ),
    path(
        "update_workflow_status",
        api_views.UpdateWorkflow.as_view(),
        name="update_workflow_status",
    ),
    path(
        "api/upload_folder",
        api_views.UploadFolder.as_view(),
        name="upload_foler",
    ),
]


app_name = "api"
