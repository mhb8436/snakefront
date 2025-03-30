from django.contrib.auth import views as auth_views
from django.contrib.auth import logout as auth_logout, authenticate, login
from django.views import generic
from django.urls import reverse_lazy

from django.shortcuts import render, redirect

from .forms import LoginForm, RegisterForm

# Create your views here.

class LoginView(auth_views.LoginView):
    form_class = LoginForm
    template_name = 'accounts/login.html'


class RegisterView(generic.CreateView):
    form_class = RegisterForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts.login')


def logout(request):
    """log the user out, either from the notebook or traditional Django auth"""
    auth_logout(request)
    return redirect("/")