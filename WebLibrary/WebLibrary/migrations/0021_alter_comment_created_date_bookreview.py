# Generated by Django 4.0.3 on 2022-03-21 16:20

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('WebLibrary', '0020_alter_comment_created_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='created_date',
            field=models.DateTimeField(default=datetime.datetime(2022, 3, 21, 18, 20, 11, 557572)),
        ),
        migrations.CreateModel(
            name='BookReview',
            fields=[
                ('review_id', models.AutoField(primary_key=True, serialize=False)),
                ('text', models.TextField(verbose_name='Review')),
                ('created_date', models.DateTimeField(default=datetime.datetime(2022, 3, 21, 18, 20, 11, 558568))),
                ('is_approved', models.BooleanField(default=False)),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='WebLibrary.book')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reviews', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-created_date',),
            },
        ),
    ]
