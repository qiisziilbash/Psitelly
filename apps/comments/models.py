import datetime
from threading import Thread

from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from apps.accounts.models import Notification
from apps.videos.models import Video


class Comment(models.Model):
    user            = models.ForeignKey(User, on_delete=models.CASCADE)
    video           = models.ForeignKey(Video, on_delete=models.CASCADE)

    parent          = models.ForeignKey('self', null=True, on_delete=models.CASCADE)

    text            = models.CharField(max_length=500, null=True)
    likes           = models.IntegerField(default=0)
    time            = models.DateTimeField(null=True)


class CommentLike(models.Model):
    user            = models.ForeignKey(User, on_delete=models.CASCADE)
    comment         = models.ForeignKey(Comment, on_delete=models.CASCADE)
    time            = models.DateTimeField()


@receiver(post_save, sender=Comment)
def increase_comments(sender, instance, created, **kwargs):
    if created:
        instance.user.profile.nComments += 1
        instance.user.profile.save()

        instance.video.comments += 1
        instance.video.save()

        send_comment_notification(instance)


@receiver(post_delete, sender=Comment)
def decrease_comments(sender, instance, *args, **kwargs):
    instance.user.profile.nComments -= 1
    instance.user.profile.save()

    instance.video.comments -= 1
    instance.video.save()


@receiver(post_save, sender=CommentLike)
def increase_comment_like(sender, instance, created, **kwargs):
    if created:
        instance.comment.likes += 1
        instance.comment.save()

        instance.comment.user.profile.nCommentUpVotesReceived += 1
        instance.comment.user.profile.save()

        instance.user.profile.nCommentUpVotesGiven += 1
        instance.user.profile.save()


@receiver(post_delete, sender=CommentLike)
def decrease_comment_like(sender, instance, *args, **kwargs):
    instance.comment.likes -= 1
    instance.comment.save()

    instance.comment.user.profile.nCommentUpVotesReceived -= 1
    instance.comment.user.profile.save()

    instance.user.profile.nCommentUpVotesGiven -= 1
    instance.user.profile.save()


def start_new_thread(function):
    def decorator(*args, **kwargs):
        t = Thread(target=function, args=args, kwargs=kwargs)
        t.daemon = True
        t.start()
    return decorator


@start_new_thread
def send_comment_notification(comment):
    if not comment.user.username == comment.video.user.username:
        if comment.video.user.profile.notifyComments:
            Notification.objects.create(user=comment.video.user,
                                        text='%s just commented on your video.' % comment.user.username,
                                        time=datetime.datetime.now())
            comment.video.user.profile.hasNotifications = True
            comment.video.user.profile.save()

        if comment.video.user.profile.emailComments:
            subject = 'Comment Notification (Psitelly)'
            msg = 'Dear %s\n\n' \
                  '%s just commented on your video.\n' \
                  'You are receiving this email because you have enabled email notifications in your profile. ' \
                  'You can change this setting in your profile any time.\n\n ' \
                  'Thanks,\n Psitelly' % (comment.video.user.username, comment.user.username)

            send_mail(subject, msg, 'psitelly@gmail.com', [comment.video.user.email], fail_silently=True)
