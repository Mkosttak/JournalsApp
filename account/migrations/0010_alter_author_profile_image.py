# Generated by Django 5.2.1 on 2025-05-22 12:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0009_alter_author_profile_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='author',
            name='profile_image',
            field=models.ImageField(default='author_profiles/default.png', upload_to='author_profiles'),
        ),
    ]
