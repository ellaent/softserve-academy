# Generated by Django 4.0.3 on 2022-03-20 16:17

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WebLibrary', '0013_alter_comment_created_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='created_date',
            field=models.DateTimeField(default=datetime.datetime(2022, 3, 20, 18, 17, 59, 296382)),
        ),
    ]
