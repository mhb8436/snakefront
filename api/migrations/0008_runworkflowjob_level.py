# Generated by Django 3.2.16 on 2022-12-28 03:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_runworkflowjob_reason'),
    ]

    operations = [
        migrations.AddField(
            model_name='runworkflowjob',
            name='level',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='Level'),
        ),
    ]
