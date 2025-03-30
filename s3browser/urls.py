from django.urls import path
from . import views


urlpatterns = [
    path("s3/input", views.s3_input, name="s3_input"),
    path("s3/output", views.s3_output, name="s3_output"),
    path("s3/download", views.s3_download, name="s3_download"),    
]

app_name = "s3browser"
