from django.forms import ModelForm
from project.models import Project
from django import forms


class ProjectForm(ModelForm):
    name = forms.CharField(label="Name")
    description = forms.CharField(label="Description")

    class Meta:
        model = Project
        fields = ["name", "description"]