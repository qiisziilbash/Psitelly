# Generated by Django 2.2.1 on 2019-11-28 05:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('joinDateTime', models.DateTimeField(null=True)),
                ('emailVerified', models.BooleanField(null=True)),
                ('code', models.IntegerField(default=0, null=True)),
                ('codeRequestTime', models.DateTimeField(null=True)),
                ('firstName', models.CharField(max_length=100, null=True)),
                ('lastName', models.CharField(max_length=100, null=True)),
                ('institute', models.CharField(max_length=100, null=True)),
                ('picture', models.ImageField(null=True, upload_to='')),
                ('secQuestion', models.CharField(max_length=100, null=True)),
                ('secAnswer', models.CharField(max_length=100, null=True)),
                ('nVideos', models.IntegerField(default=0, null=True)),
                ('nComments', models.IntegerField(default=0, null=True)),
                ('nFollowers', models.IntegerField(default=0, null=True)),
                ('nFollowees', models.IntegerField(default=0, null=True)),
                ('nWatchedVideos', models.IntegerField(default=0, null=True)),
                ('nVideoUpVotesReceived', models.IntegerField(default=0, null=True)),
                ('nVideoUpVotesGiven', models.IntegerField(default=0, null=True)),
                ('nCommentUpVotesReceived', models.IntegerField(default=0, null=True)),
                ('nCommentUpVotesGiven', models.IntegerField(default=0, null=True)),
                ('hasNotifications', models.BooleanField(default=False, null=True)),
                ('notifyComments', models.BooleanField(default=False, null=True)),
                ('notifyMentions', models.BooleanField(default=False, null=True)),
                ('notifyFollows', models.BooleanField(default=False, null=True)),
                ('notifyUploads', models.BooleanField(default=False, null=True)),
                ('emailComments', models.BooleanField(default=False, null=True)),
                ('emailMentions', models.BooleanField(default=False, null=True)),
                ('emailFollows', models.BooleanField(default=False, null=True)),
                ('emailUploads', models.BooleanField(default=False, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserFollowing',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(null=True)),
                ('followee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='userfollowing_followee', to='accounts.Profile')),
                ('follower', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='userfollowing_follower', to='accounts.Profile')),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=500, null=True)),
                ('seen', models.BooleanField(default=False, null=True)),
                ('time', models.DateTimeField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
