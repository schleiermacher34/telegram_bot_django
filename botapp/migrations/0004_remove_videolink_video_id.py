# Generated by Django 5.1 on 2024-09-26 08:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('botapp', '0003_videolink_video_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='videolink',
            name='video_id',
        ),
    ]
