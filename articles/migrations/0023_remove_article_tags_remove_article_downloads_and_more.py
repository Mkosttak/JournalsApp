# Generated by Django 5.2.1 on 2025-05-21 08:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0022_notification'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='article',
            name='tags',
        ),
        migrations.RemoveField(
            model_name='article',
            name='downloads',
        ),
        migrations.RemoveField(
            model_name='article',
            name='likes',
        ),
        migrations.RemoveField(
            model_name='article',
            name='shares',
        ),
        migrations.RemoveField(
            model_name='article',
            name='views',
        ),
        migrations.DeleteModel(
            name='Notification',
        ),
        migrations.DeleteModel(
            name='Tag',
        ),
    ]
