from django.conf.urls import url, include
from accounts import views

urlpatterns = [
    url(r"^login/$", views.LoginView.as_view(), name="login"),
    url(r"^register/$", views.RegisterView.as_view(), name='register'),
    url(r"^logout/$", views.logout, name="logout"),    
]

app_name="accounts"