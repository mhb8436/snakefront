from django.forms import ModelForm
from main.models import Workflow
from main.utils import get_workdir_choices
from django import forms
from snakefront.settings import cfg


class WorkflowForm(ModelForm):
    workdirs = forms.ChoiceField(choices=get_workdir_choices())

    class Meta:
        model = Workflow

        # Notebooks are always implicitly private, there is only one user
        if cfg.NOTEBOOK:
            fields = ["name", "workdirs"]
        else:
            fields = ["name", "workdirs", "private"]
