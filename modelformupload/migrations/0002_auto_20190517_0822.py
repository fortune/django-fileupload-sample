# Generated by Django 2.2.1 on 2019-05-17 08:22

from django.db import migrations, models
import modelformupload.models


class Migration(migrations.Migration):

    dependencies = [
        ('modelformupload', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fileuploadmodel',
            name='document',
            field=models.FileField(max_length=200, upload_to=modelformupload.models.get_upload_to),
        ),
    ]
