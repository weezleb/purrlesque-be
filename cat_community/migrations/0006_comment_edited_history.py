# Generated by Django 4.2.7 on 2023-11-30 18:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cat_community', '0005_comment_thread_alter_comment_cat_photo'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='edited_history',
            field=models.JSONField(default=list),
        ),
    ]