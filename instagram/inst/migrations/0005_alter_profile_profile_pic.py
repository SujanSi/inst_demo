# Generated by Django 5.0.6 on 2024-06-14 08:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inst', '0004_alter_profile_profile_pic'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='profile_pic',
            field=models.ImageField(blank=True, upload_to='profile_pic/'),
        ),
    ]
