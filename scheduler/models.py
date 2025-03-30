from django.db import models
from main.models import Workflow
from datetime import datetime
from snakefront.settings import cfg
# Create your models here.
from django.db.models.signals import post_save
from django.dispatch import receiver
import os

class DBTest(models.Model):    
    odate = models.CharField("working date", max_length=500, blank=True, null=True)
    data = models.TextField("Data", blank=True, null=True)
    updated_at = models.DateTimeField("Update Date", auto_now_add=True)
    

    def __str__(self):
        return self.odate
    
    class Meta:
        app_label = "scheduler"


