# Generated by Django 4.2.6 on 2023-10-24 13:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_requestparticipant_is_capitan'),
    ]

    operations = [
        migrations.AddField(
            model_name='participant',
            name='file_extension',
            field=models.CharField(default='jpg', max_length=10, verbose_name='Расширение файла изображения'),
        ),
    ]
