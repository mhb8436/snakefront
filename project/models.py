from cgi import print_form
from django.db.models.signals import pre_save
from django.db import models

from django.conf import settings
from django.urls import reverse
from django.contrib.postgres.fields import JSONField as DjangoJSONField

from main.utils import CommandRunner, write_file, get_tmpfile, read_file
from snakefront.argparser import SnakefaceParser
from snakefront.settings import cfg
from django.db.models import Field

import itertools
import json
import os
from django.utils.translation import gettext_lazy as _
import uuid

# Create your models here.
class Project(models.Model):
    """ A Project is parent of Workflows     
    """
    uuid = models.UUIDField(
        _("ID"), 
        primary_key = True, 
        default = uuid.uuid4, 
        editable=False
    )

    name = models.CharField(
        _("Name"), max_length=255, blank=False, null=True
    )

    description = models.TextField(
        _("Description"), blank=True, null=True
    )
    
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)

    def __str__(self):
        return self.name

    