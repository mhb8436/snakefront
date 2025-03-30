
from django.conf.urls import include, url
from django.contrib import admin
from django.urls import path
from django.views.generic.base import TemplateView

from base import urls as base_urls
from main import urls as main_urls
# from users import urls as user_urls
from api import urls as api_urls
from accounts import urls as accounts_urls
from project import urls as project_urls
from scheduler import urls as scheduler_urls
from s3browser import urls as s3browser_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r"^", include(base_urls, namespace="base")),
    url(r"^", include(api_urls, namespace="api")),
    url(r"^", include(main_urls, namespace="main")),
    # url(r"^", include(user_urls, namespace="users")),
    url(r"^", include(accounts_urls, namespace="accounts")),
    url(r"^", include(project_urls, namespace="project")),
    url(r"^", include(scheduler_urls, namespace="scheduler")),
    url(r"^", include(s3browser_urls, namespace="s3browser")),
    url(
        r"^robots\.txt?/$",
        TemplateView.as_view(
            template_name="base/robots.txt", content_type="text/plain"
        ),
    ),
]
