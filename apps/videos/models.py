import datetime
import os
from threading import Thread

from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.core.mail import send_mail
from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from taggit.managers import TaggableManager

from Psitelly.settings import MEDIA_ROOT
from apps.accounts.models import UserFollowing, Notification


class Focus(models.Model):
    title = models.CharField(max_length=100)
    nFollowers = models.IntegerField(default=0, null=True)
    nVideos = models.IntegerField(default=0, null=True)


class Topic(models.Model):
    title = models.CharField(max_length=100)
    nFollowers = models.IntegerField(default=0, null=True)
    nVideos = models.IntegerField(default=0, null=True)


class Journal(models.Model):
    title = models.CharField(max_length=100)
    nFollowers = models.IntegerField(default=0, null=True)
    nVideos = models.IntegerField(default=0, null=True)


class Author(models.Model):
    title = models.CharField(max_length=100)
    lastName = models.CharField(max_length=100)
    nFollowers = models.IntegerField(default=0, null=True)
    nVideos = models.IntegerField(default=0, null=True)


class Video(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    title = models.CharField(max_length=500, null=True)
    year = models.IntegerField(default=0)

    focus = models.ForeignKey(Focus, on_delete=models.SET_NULL, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    journal = models.ForeignKey(Journal, on_delete=models.SET_NULL, null=True)
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True)

    pdfLink = models.CharField(max_length=200, null=True)
    gsLink = models.CharField(max_length=200, null=True)
    description = models.CharField(max_length=1000, null=True)

    duration = models.DurationField(null=True)
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    comments = models.IntegerField(default=0)
    publishDate = models.DateTimeField(null=True)

    videoFile = models.FileField()
    videoFile720 = models.FileField(null=True)
    videoFile480 = models.FileField(null=True)
    videoFile360 = models.FileField(null=True)

    thumbnail = models.ImageField(null=True)

    isProcessed = models.BooleanField(default=False)

    tags = TaggableManager()

    def formatted_duration(self):
        secs_t = self.duration.total_seconds()
        mins = int((secs_t / 60) % 60)
        secs = secs_t - (60 * mins)
        return '%02d:%02d' % (mins, secs)


class VideoLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    time = models.DateTimeField()


class AuthorFollowing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    time = models.DateTimeField()


class TopicFollowing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    time = models.DateTimeField()


class JournalFollowing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    journal = models.ForeignKey(Journal, on_delete=models.CASCADE)
    time = models.DateTimeField()


class FocusFollowing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    focus = models.ForeignKey(Focus, on_delete=models.CASCADE)
    time = models.DateTimeField()


class WatchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    time = models.DateTimeField()
    invisible = models.BooleanField(default=False, null=True)


class WatchLater(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    time = models.DateTimeField()


@receiver(post_save, sender=Video)
def increase_videos(sender, instance, created, **kwargs):
    if created:
        instance.focus.nVideos += 1
        instance.topic.nVideos += 1
        instance.journal.nVideos += 1
        instance.author.nVideos += 1

        instance.focus.save()
        instance.topic.save()
        instance.journal.save()
        instance.author.save()

        instance.user.profile.nVideos += 1
        instance.user.profile.save()

        send_upload_notifications(instance)


@receiver(post_delete, sender=Video)
def decrease_videos(sender, instance, *args, **kwargs):
    fs = FileSystemStorage()

    try:
        fs.delete(os.path.join(MEDIA_ROOT, 'videos/{0}'.format(os.path.basename(instance.videoFile.name))))
        fs.delete(os.path.join(MEDIA_ROOT, 'videos/{0}'.format(os.path.basename(instance.videoFile720.name))))
        fs.delete(os.path.join(MEDIA_ROOT, 'videos/{0}'.format(os.path.basename(instance.videoFile480.name))))
        fs.delete(os.path.join(MEDIA_ROOT, 'videos/{0}'.format(os.path.basename(instance.videoFile360.name))))
        fs.delete(os.path.join(MEDIA_ROOT, 'thumbnails/{0}'.format(os.path.basename(instance.thumbnail.name))))
    except:
        pass

    instance.tags.clear()

    instance.focus.nVideos -= 1
    instance.topic.nVideos -= 1
    instance.journal.nVideos -= 1
    instance.author.nVideos -= 1

    instance.focus.save()
    instance.topic.save()
    instance.journal.save()
    instance.author.save()

    instance.user.profile.nVideos -= 1
    instance.user.profile.save()

    if instance.focus.nVideos == 0:
        Focus.objects.filter(title=instance.focus.title).delete()
    if instance.topic.nVideos == 0:
        Topic.objects.filter(title=instance.topic.title).delete()
    if instance.journal.nVideos == 0:
        Journal.objects.filter(title=instance.journal.title).delete()
    if instance.author.nVideos == 0:
        Author.objects.filter(title=instance.author.title).delete()


@receiver(post_save, sender=FocusFollowing)
def increase_focus_followers(sender, instance, created, **kwargs):
    if created:
        instance.focus.nFollowers += 1
        instance.focus.save()

        instance.user.profile.nFollowees += 1
        instance.user.profile.save()


@receiver(post_save, sender=TopicFollowing)
def increase_topic_followers(sender, instance, created, **kwargs):
    if created:
        instance.topic.nFollowers += 1
        instance.topic.save()

        instance.user.profile.nFollowees += 1
        instance.user.profile.save()


@receiver(post_save, sender=JournalFollowing)
def increase_journal_followers(sender, instance, created, **kwargs):
    if created:
        instance.journal.nFollowers += 1
        instance.journal.save()

        instance.user.profile.nFollowees += 1
        instance.user.profile.save()


@receiver(post_save, sender=AuthorFollowing)
def increase_author_followers(sender, instance, created, **kwargs):
    if created:
        instance.author.nFollowers += 1
        instance.author.save()

        instance.user.profile.nFollowees += 1
        instance.user.profile.save()


@receiver(post_delete, sender=FocusFollowing)
def decrease_focus_followers(sender, instance, *args, **kwargs):
    instance.focus.nFollowers -= 1
    instance.focus.save()

    instance.user.profile.nFollowees -= 1
    instance.user.profile.save()


@receiver(post_delete, sender=TopicFollowing)
def decrease_topic_followers(sender, instance, *args, **kwargs):
    instance.topic.nFollowers -= 1
    instance.topic.save()

    instance.user.profile.nFollowees -= 1
    instance.user.profile.save()


@receiver(post_delete, sender=JournalFollowing)
def decrease_journal_followers(sender, instance, *args, **kwargs):
    instance.journal.nFollowers -= 1
    instance.journal.save()

    instance.user.profile.nFollowees -= 1
    instance.user.profile.save()


@receiver(post_delete, sender=AuthorFollowing)
def decrease_author_followers(sender, instance, *args, **kwargs):
    instance.author.nFollowers -= 1
    instance.author.save()

    instance.user.profile.nFollowees -= 1
    instance.user.profile.save()


@receiver(post_save, sender=WatchHistory)
def increase_watch_history(sender, instance, created, **kwargs):
    if created:
        instance.user.profile.nWatchedVideos += 1
        instance.user.profile.save()
        instance.video.views += 1
        instance.video.save()


@receiver(post_save, sender=VideoLike)
def increase_video_like(sender, instance, created, **kwargs):
    if created:
        instance.video.likes += 1
        instance.video.save()

        instance.video.user.profile.nVideoUpVotesReceived += 1
        instance.video.user.profile.save()

        instance.user.profile.nVideoUpVotesGiven += 1
        instance.user.profile.save()


@receiver(post_delete, sender=VideoLike)
def decrease_video_like(sender, instance, *args, **kwargs):
    instance.video.likes -= 1
    instance.video.save()

    instance.video.user.profile.nVideoUpVotesReceived -= 1
    instance.video.user.profile.save()

    instance.user.profile.nVideoUpVotesGiven -= 1
    instance.user.profile.save()


def start_new_thread(function):
    def decorator(*args, **kwargs):
        t = Thread(target=function, args=args, kwargs=kwargs)
        t.daemon = True
        t.start()

    return decorator


@start_new_thread
def send_upload_notifications(video):
    userFollowings = UserFollowing.objects.filter(followee=video.user.profile)

    if userFollowings:
        for userFollowing in userFollowings:
            if userFollowing.follower.notifyUploads:
                Notification.objects.create(user=userFollowing.follower.user,
                                            publisher=userFollowing.followee.user.username,
                                            itemID=video.pk,
                                            text=video.title,
                                            type="User Video Upload",
                                            time=datetime.datetime.now())
                userFollowing.follower.user.profile.hasNotifications = True
                userFollowing.follower.user.profile.save()

            if userFollowing.follower.emailFollows:
                subject = 'Upload Notification (Psitelly)'
                msg = 'Dear %s\n\n' \
                      '%s just uploaded a new video.\n' \
                      'You are receiving this email because you have enabled email notifications in your profile.' \
                      'You can change this setting in your profile any time.\n\n ' \
                      'Thanks,\n Psitelly' % (userFollowing.follower.user.username,
                                              userFollowing.followee.user.username)

                send_mail(subject, msg, 'psitelly@gmail.com', [userFollowing.follower.user.email], fail_silently=True)

    focusFollowings = FocusFollowing.objects.filter(focus=video.focus)

    if focusFollowings:
        for focusFollowing in focusFollowings:
            if not focusFollowing.user.username == video.user.username:
                if focusFollowing.user.profile.notifyUploads:
                    Notification.objects.create(user=focusFollowing.user,
                                                publisher=focusFollowing.focus.title,
                                                type="Focus Video Upload",
                                                itemID=video.pk,
                                                text=video.title,
                                                time=datetime.datetime.now())
                    focusFollowing.user.profile.hasNotifications = True
                    focusFollowing.user.profile.save()

                if focusFollowing.user.profile.emailFollows:
                    subject = 'Upload Notification (Psitelly)'
                    msg = 'Dear %s\n\n' \
                          'A video has been uploaded with %s focus.\n' \
                          'You are receiving this email because you have enabled email notifications in your profile.' \
                          'You can change this setting in your profile any time.\n\n ' \
                          'Thanks,\n Psitelly' % (focusFollowing.user.username,
                                                  focusFollowing.focus.title)

                    send_mail(subject, msg, 'psitelly@gmail.com', [focusFollowing.user.email], fail_silently=True)

    journalFollowings = JournalFollowing.objects.filter(journal=video.journal)

    if journalFollowings:
        for journalFollowing in journalFollowings:
            if not journalFollowing.user.username == video.user.username:
                if journalFollowing.user.profile.notifyUploads:
                    Notification.objects.create(user=journalFollowing.user,
                                                publisher=journalFollowing.journal.title,
                                                type="Journal Video Upload",
                                                itemID=video.pk,
                                                text=video.title,
                                                time=datetime.datetime.now())
                    journalFollowing.user.profile.hasNotifications = True
                    journalFollowing.user.profile.save()

                if journalFollowing.user.profile.emailFollows:
                    subject = 'Upload Notification (Psitelly)'
                    msg = 'Dear %s\n\n' \
                          'A video has been uploaded in %s journal.\n' \
                          'You are receiving this email because you have enabled email notifications in your profile.' \
                          'You can change this setting in your profile any time.\n\n ' \
                          'Thanks,\n Psitelly' % (journalFollowing.user.username,
                                                  journalFollowing.journal.title)

                    send_mail(subject, msg, 'psitelly@gmail.com', [journalFollowing.user.email], fail_silently=True)

    topicFollowings = TopicFollowing.objects.filter(topic=video.topic)

    if topicFollowings:
        for topicFollowing in topicFollowings:
            if not topicFollowing.user.username == video.user.username:
                if topicFollowing.user.profile.notifyUploads:
                    Notification.objects.create(user=topicFollowing.user,
                                                publisher=topicFollowing.topic.title,
                                                type="Topic Video Upload",
                                                itemID=video.pk,
                                                text=video.title,
                                                time=datetime.datetime.now())
                    topicFollowing.user.profile.hasNotifications = True
                    topicFollowing.user.profile.save()

                if topicFollowing.user.profile.emailFollows:
                    subject = 'Upload Notification (Psitelly)'
                    msg = 'Dear %s\n\n' \
                          'A video has been uploaded by %s topic.\n' \
                          'You are receiving this email because you have enabled email notifications in your profile.' \
                          'You can change this setting in your profile any time.\n\n ' \
                          'Thanks,\n Psitelly' % (topicFollowing.user.username,
                                                  topicFollowing.topic.title)

                    send_mail(subject, msg, 'psitelly@gmail.com', [topicFollowing.user.email], fail_silently=True)

    authorFollowings = AuthorFollowing.objects.filter(author=video.author)

    if authorFollowings:
        for authorFollowing in authorFollowings:
            if not authorFollowing.user.username == video.user.username:
                if authorFollowing.user.profile.notifyUploads:
                    Notification.objects.create(user=AuthorFollowing.user,
                                                publisher=AuthorFollowing.author.title,
                                                type="Author Video Upload",
                                                itemID=video.pk,
                                                text=video.title,
                                                time=datetime.datetime.now())
                    authorFollowing.user.profile.hasNotifications = True
                    authorFollowing.user.profile.save()

                if authorFollowing.user.profile.emailFollows:
                    subject = 'Upload Notification (Psitelly)'
                    msg = 'Dear %s\n\n' \
                          'A video has been uploaded by %s topic.\n' \
                          'You are receiving this email because you have enabled email notifications in your profile.' \
                          'You can change this setting in your profile any time.\n\n ' \
                          'Thanks,\n Psitelly' % (authorFollowing.user.username,
                                                  authorFollowing.author.title)

                    send_mail(subject, msg, 'psitelly@gmail.com', [authorFollowing.user.email], fail_silently=True)
