# Generated by Django 4.2.7 on 2023-11-30 00:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cat_community', '0004_comment_delete_post'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='thread',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='cat_community.thread'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='cat_photo',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='cat_community.catphoto'),
        ),
    ]
