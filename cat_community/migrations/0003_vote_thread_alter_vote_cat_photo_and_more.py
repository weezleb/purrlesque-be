# Generated by Django 4.2.7 on 2023-11-22 17:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cat_community', '0002_vote'),
    ]

    operations = [
        migrations.AddField(
            model_name='vote',
            name='thread',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='cat_community.thread'),
        ),
        migrations.AlterField(
            model_name='vote',
            name='cat_photo',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='cat_community.catphoto'),
        ),
        migrations.AlterField(
            model_name='vote',
            name='vote_type',
            field=models.CharField(choices=[('up', 'Upvote'), ('down', 'Downvote')], max_length=10),
        ),
    ]
