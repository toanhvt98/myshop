# Generated by Django 5.2.1 on 2025-05-25 08:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_app', '0004_alter_oauth2token_access_token_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='birth_day',
            new_name='birth_date',
        ),
    ]
