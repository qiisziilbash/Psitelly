import datetime
from threading import Thread

from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.core.mail import send_mail
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


class Profile(models.Model):
    user            = models.OneToOneField(User, on_delete=models.CASCADE)

    joinDateTime    = models.DateTimeField(null=True)

    emailVerified   = models.BooleanField(null=True)
    code            = models.IntegerField(default=0, null=True)
    codeRequestTime = models.DateTimeField(null=True)

    firstName       = models.CharField(max_length=100, null=True)
    lastName        = models.CharField(max_length=100, null=True)
    institute       = models.CharField(max_length=100, null=True)

    picture         = models.ImageField(null=True)

    secQuestion     = models.CharField(max_length=100, null=True)
    secAnswer       = models.CharField(max_length=100, null=True)

    nVideos         = models.IntegerField(default=0, null=True)
    nComments       = models.IntegerField(default=0, null=True)
    nFollowers      = models.IntegerField(default=0, null=True)
    nFollowees      = models.IntegerField(default=0, null=True)

    nWatchedVideos          = models.IntegerField(default=0, null=True)

    nVideoUpVotesReceived   = models.IntegerField(default=0, null=True)
    nVideoUpVotesGiven      = models.IntegerField(default=0, null=True)

    nCommentUpVotesReceived = models.IntegerField(default=0, null=True)
    nCommentUpVotesGiven    = models.IntegerField(default=0, null=True)

    hasNotifications        = models.BooleanField(default=False, null=True)

    notifyComments  = models.BooleanField(default=False, null=True)
    notifyMentions          = models.BooleanField(default=False, null=True)
    notifyFollows           = models.BooleanField(default=False, null=True)
    notifyUploads           = models.BooleanField(default=False, null=True)

    emailComments  = models.BooleanField(default=False, null=True)
    emailMentions          = models.BooleanField(default=False, null=True)
    emailFollows           = models.BooleanField(default=False, null=True)
    emailUploads           = models.BooleanField(default=False, null=True)


class UserFollowing(models.Model):
    follower        = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='%(class)s_follower')
    followee        = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='%(class)s_followee')
    time            = models.DateTimeField(null=True)


class Notification(models.Model):
    user        = models.ForeignKey(User, on_delete=models.CASCADE)
    text        = models.CharField(max_length=500, null=True)
    seen        = models.BooleanField(default=False, null=True)
    time        = models.DateTimeField()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        instance.profile.joinDateTime = datetime.datetime.now()
        fs = FileSystemStorage()
        instance.profile.picture = fs.url('profiles/avatar-active.png')
        instance.profile.save()


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


@receiver(post_save, sender=UserFollowing)
def increase_user_followers(sender, instance, created, **kwargs):
    if created:
        instance.follower.nFollowees += 1
        instance.followee.nFollowers += 1
        instance.follower.save()
        instance.followee.save()

        send_follow_notification(instance)


@receiver(post_delete, sender=UserFollowing)
def decrease_user_followers(sender, instance, *args, **kwargs):
    instance.follower.nFollowees -= 1
    instance.followee.nFollowers -= 1
    instance.follower.save()
    instance.followee.save()


def start_new_thread(function):
    def decorator(*args, **kwargs):
        t = Thread(target=function, args=args, kwargs=kwargs)
        t.daemon = True
        t.start()
    return decorator


@start_new_thread
def send_follow_notification(userFollowing):
    if userFollowing.followee.notifyFollows:
        Notification.objects.create(user=userFollowing.followee.user,
                                    text='%s just started to follow you.' % userFollowing.follower.user.username,
                                    time=datetime.datetime.now())
        userFollowing.followee.hasNotifications = True
        userFollowing.followee.save()
    

    if userFollowing.followee.emailFollows:
        subject = 'Follow Notification (Psitelly) '
        msg = 'Dear %s\n\n' \
              '%s just started to follow you.\n' \
              'You are receiving this email because you have enabled email notifications in your profile. ' \
              'You can change this setting in your profile any time.\n\n ' \
              'Thanks,\n Psitelly' % (userFollowing.followee.user.username, userFollowing.follower.user.username)

        send_mail(subject, msg, 'psitelly@gmail.com', [userFollowing.followee.user.email], fail_silently=True)