from django.conf.urls import url, include
from users import views
# from social_django import urls as social_urls

urlpatterns = [
    #    url(r"^login/$", views.login, name="login"),
    url(r"^login/notebook/$", views.notebook_login, name="notebook_login"),
    # url(r"^accounts/login/$", views.login),
    url(r"^logout/$", views.logout, name="logout"),
    # url("", include(social_urls, namespace="social")),
]

app_name = "users"
