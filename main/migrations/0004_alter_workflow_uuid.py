# Generated by Django 3.2.16 on 2022-12-06 08:19

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_alter_workflow_uuid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workflow',
            name='uuid',
            field=models.UUIDField(blank=True, default=uuid.UUID('c4807977-6e06-40ed-afcf-f9a066dbd815'), editable=False, null=True, verbose_name='UUID'),
        ),
    ]
