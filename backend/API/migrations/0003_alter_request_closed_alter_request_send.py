# Generated by Django 4.2.6 on 2023-10-10 23:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_alter_user_is_manager'),
    ]

    operations = [
        migrations.AlterField(
            model_name='request',
            name='closed',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Закрытие'),
        ),
        migrations.AlterField(
            model_name='request',
            name='send',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Отправка'),
        ),
    ]
