# Generated by Django 4.0.3 on 2022-03-20 16:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_alter_user_role'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(1, 'Main'), (2, (('edit', 'Editing mode'), ('non-edit', 'Non-editing mode'))), (3, 'Super')], null=True),
        ),
    ]
