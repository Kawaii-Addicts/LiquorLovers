# Generated by Django 4.1.5 on 2023-01-10 18:26

import LiquorLovers.utils
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='pfp',
            field=models.ImageField(default='defaults/pfps/default.png', upload_to=LiquorLovers.utils.uuid_upload_to),
        ),
    ]