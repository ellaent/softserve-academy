# Generated by Django 4.0.3 on 2022-03-21 16:19

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WebLibrary', '0019_alter_comment_created_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='created_date',
            field=models.DateTimeField(default=datetime.datetime(2022, 3, 21, 18, 19, 0, 449936)),
        ),
    ]
