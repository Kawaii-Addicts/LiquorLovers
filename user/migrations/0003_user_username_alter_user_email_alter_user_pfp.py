# Generated by Django 4.1.6 on 2023-02-09 20:18

import LiquorLovers.utils
import django.contrib.auth.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_alter_user_pfp'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='username',
            field=models.CharField(editable=False, max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()]),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(editable=False, max_length=254, unique=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='pfp',
            field=models.ImageField(default='defaults/pfps/default.png', upload_to=LiquorLovers.utils.uuid_upload_to),
        ),
    ]
