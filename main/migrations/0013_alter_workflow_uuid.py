# Generated by Django 3.2.16 on 2022-12-30 00:56

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_alter_workflow_uuid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workflow',
            name='uuid',
            field=models.UUIDField(blank=True, default=uuid.UUID('1c9d3449-6107-4e70-929c-05364c41b989'), editable=False, null=True, verbose_name='UUID'),
        ),
    ]
