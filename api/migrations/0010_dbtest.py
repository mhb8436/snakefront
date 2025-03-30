# Generated by Django 3.2.16 on 2022-12-30 00:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_auto_20221228_1645'),
    ]

    operations = [
        migrations.CreateModel(
            name='DBTest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('odate', models.CharField(blank=True, max_length=500, null=True, verbose_name='working date')),
                ('data', models.TextField(blank=True, null=True, verbose_name='Data')),
                ('updated_at', models.DateTimeField(auto_now_add=True, verbose_name='Update Date')),
            ],
        ),
    ]
