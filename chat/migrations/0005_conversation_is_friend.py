# Generated by Django 4.2 on 2024-05-10 17:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0004_rename_message_content_message_message_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='conversation',
            name='is_friend',
            field=models.IntegerField(choices=[(0, 'false'), (1, 'pending'), (2, 'true')], default=0),
        ),
    ]
