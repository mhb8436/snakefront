# Generated by Django 3.2.16 on 2022-12-28 03:17

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0010_alter_workflow_uuid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workflow',
            name='uuid',
            field=models.UUIDField(blank=True, default=uuid.UUID('7041755b-1af2-4fa5-a3eb-4e52712e0b16'), editable=False, null=True, verbose_name='UUID'),
        ),
    ]
