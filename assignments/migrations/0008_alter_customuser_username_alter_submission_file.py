# Generated by Django 4.2.4 on 2023-09-11 08:07

import assignments.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assignments', '0007_submission_score'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='username',
            field=models.TextField(max_length=30),
        ),
        migrations.AlterField(
            model_name='submission',
            name='file',
            field=models.FileField(upload_to=assignments.models.generate_file_name),
        ),
    ]