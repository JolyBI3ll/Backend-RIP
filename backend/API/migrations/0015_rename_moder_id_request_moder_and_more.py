# Generated by Django 4.2.6 on 2023-11-20 12:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0014_alter_request_status'),
    ]

    operations = [
        migrations.RenameField(
            model_name='request',
            old_name='moder_id',
            new_name='moder',
        ),
        migrations.RenameField(
            model_name='request',
            old_name='user_id',
            new_name='user',
        ),
    ]
