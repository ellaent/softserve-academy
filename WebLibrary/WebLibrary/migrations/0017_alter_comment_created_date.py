# Generated by Django 4.0.3 on 2022-03-20 18:10

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WebLibrary', '0016_alter_comment_created_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='created_date',
            field=models.DateTimeField(default=datetime.datetime(2022, 3, 20, 20, 10, 37, 54713)),
        ),
    ]
