import random
from urllib.parse import urlencode

from moviepy.editor import *

from apps.comments.models import Comment
from apps.comments.views import get_liked_comments
from apps.information.models import News
from apps.videos.models import *

from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse


def upload_video(request):
    if request.method == "GET":
        context = {'newses': News.objects.order_by('-time')[:5],
                   'Statistics': True,
                   'usersCount': User.objects.filter().count(),
                   'videosCount': Video.objects.filter().count(),
                   'journalCount': Journal.objects.filter().count(),
                   'authorCount': Author.objects.filter().count(),
                   'topicCount': Topic.objects.filter().count(),
                   'focusCount': Focus.objects.filter().count(),
                   'journals': Journal.objects.all(),
                   'focuses': Focus.objects.all(),
                   'topics': Topic.objects.all(),
                   'authors': Author.objects.all()
                   }

        return render(request, 'videos/Upload_Video.html', context)

    if request.method == "POST":
        if 'videoFile' in request.FILES:
            file = request.FILES['videoFile']

            video_suffix = os.path.splitext(file.name)[1]
            random_suffix = '_' + str(random.randint(1, 100000000)) + str(random.randint(1, 100000000))

            videoFile, thumbnailFile, duration, err = save_video(file, random_suffix, video_suffix)

            if not err:
                focus = request.POST.get('focus', '')
                topic = request.POST.get('topic', '')
                journal = request.POST.get('journal', '')
                author = request.POST.get('author', '')

                if not Focus.objects.filter(title=focus).exists():
                    Focus.objects.create(title=focus)

                if not Topic.objects.filter(title=topic).exists():
                    Topic.objects.create(title=topic)

                if not Journal.objects.filter(title=journal).exists():
                    Journal.objects.create(title=journal)

                if not Author.objects.filter(title=author).exists():
                    Author.objects.create(title=author, lastName=author.split(" ")[-1])

                video = Video.objects.create(user=request.user, videoFile=videoFile, thumbnail=thumbnailFile,
                                             duration=datetime.timedelta(seconds=duration),
                                             publishDate=datetime.datetime.now(), title=request.POST.get('title', ''),
                                             description=request.POST.get('description', ''),
                                             gsLink=request.POST.get('gs', ''), pdfLink=request.POST.get('link', ''),
                                             author=Author.objects.get(title=author), year=request.POST.get('year', 0),
                                             journal=Journal.objects.get(title=journal),
                                             focus=Focus.objects.get(title=focus), topic=Topic.objects.get(title=topic))

                add_tags(video)

                create_different_video_qualities(video, random_suffix, video_suffix)

        return redirect('{}?{}'.format(reverse('index'), urlencode({'content': 'My Videos'})))


def edit_video(request):
    if request.user.is_authenticated:
        if request.method == 'GET':
            videoPK = request.GET.get('videoPK', '')
            context = {
                'newses': News.objects.order_by('-time')[:5],
                'Statistics': True,
                'usersCount': User.objects.filter().count(),
                'videosCount': Video.objects.filter().count(),
                'journalCount': Journal.objects.filter().count(),
                'authorCount': Author.objects.filter().count(),
                'topicCount': Topic.objects.filter().count(),
                'focusCount': Focus.objects.filter().count(),
                'journals': Journal.objects.all(),
                'focuses': Focus.objects.all(),
                'topics': Topic.objects.all(),
                'authors': Author.objects.all()
            }

            video = Video.objects.get(pk=videoPK)
            context['video'] = video
            return render(request, 'videos/Edit_Video.html', context)

        if request.method == 'POST':
            videoPK = request.POST.get('videoPK', ' ')
            video = Video.objects.get(pk=videoPK)

            focus = request.POST.get('focus', '')
            topic = request.POST.get('topic', '')
            journal = request.POST.get('journal', '')
            author = request.POST.get('author', '')

            if not video.focus.title == focus:
                fObj = Focus.objects.get(title=video.focus.title)

                if fObj.nVideos == 1:
                    Focus.objects.filter(title=video.focus.title).delete()
                else:
                    fObj.nVideos -= 1
                    fObj.save()

                if not Focus.objects.filter(title=focus).exists():
                    Focus.objects.create(title=focus)

                focusObject = Focus.objects.get(title=focus)
                focusObject.nVideos += 1
                focusObject.save()

                Video.objects.filter(pk=videoPK).update(focus=focusObject)

            if not video.topic.title == topic:
                tObj = Topic.objects.get(title=video.topic.title)

                if tObj.nVideos == 1:
                    Topic.objects.filter(title=video.topic.title).delete()
                else:
                    tObj.nVideos -= 1
                    tObj.save()

                if not Topic.objects.filter(title=topic).exists():
                    Topic.objects.create(title=topic)

                topicObject = Topic.objects.get(title=topic)
                topicObject.nVideos += 1
                topicObject.save()

                Video.objects.filter(pk=videoPK).update(topic=topicObject)

            if not video.journal.title == journal:
                jObj = Journal.objects.get(title=video.journal.title)

                if jObj.nVideos == 1:
                    Journal.objects.filter(title=video.journal.title).delete()
                else:
                    jObj.nVideos -= 1
                    jObj.save()

                if not Journal.objects.filter(title=journal).exists():
                    Journal.objects.create(title=journal)

                journalObject = Journal.objects.get(title=journal)
                journalObject.nVideos += 1
                journalObject.save()

                Video.objects.filter(pk=videoPK).update(journal=journalObject)

            if not video.author.title == author:
                aObj = Author.objects.get(title=video.author.title)

                if aObj.nVideos == 1:
                    Author.objects.filter(title=video.author.title).delete()
                else:
                    aObj.nVideos -= 1
                    aObj.save()

                if not Author.objects.filter(title=author).exists():
                    Author.objects.create(title=author, lastName=author.split(" ")[-1])

                authorObject = Author.objects.get(title=author)
                authorObject.nVideos += 1
                authorObject.save()

                Video.objects.filter(pk=videoPK).update(author=authorObject)

            Video.objects.filter(pk=videoPK).update(title=request.POST.get('title', ''),
                                                    year=request.POST.get('year', 0),
                                                    description=request.POST.get('description', ''),
                                                    gsLink=request.POST.get('gs', ''),
                                                    pdfLink=request.POST.get('link', ''))
            video = Video.objects.get(pk=videoPK)
            video.tags.clear()
            add_tags(video)

            if 'videoFile' in request.FILES and video.isProcessed:
                file = request.FILES['videoFile']

                video_suffix = os.path.splitext(file.name)[1]
                random_suffix = '_' + str(random.randint(1, 100000000)) + str(random.randint(1, 100000000))

                v, t, d, err = save_video(file, random_suffix, video_suffix)

                if not err:
                    delete_old_videos(video)

                video.videoFile = v
                video.thumbnail = t
                video.duration = datetime.timedelta(seconds=d)
                video.publishDate = datetime.datetime.now()
                video.videoFile720 = ''
                video.isProcessed = False

                video.save()

                create_different_video_qualities(video, random_suffix, video_suffix)

            return redirect('{}?{}'.format(reverse('index'), urlencode({'content': 'My Videos'})))
    else:
        return redirect('{}?{}'.format(reverse('index'), urlencode({'content': 'My Videos'})))


def play_video(request):
    if request.method == "GET":
        context = {'newses': News.objects.order_by('-time')[:5],
                   'Statistics': True,
                   'usersCount': User.objects.filter().count(),
                   'videosCount': Video.objects.filter().count(),
                   'journalCount': Journal.objects.filter().count(),
                   'authorCount': Author.objects.filter().count(),
                   'topicCount': Topic.objects.filter().count(),
                   'focusCount': Focus.objects.filter().count(),
                   }

        videoPK = request.GET.get('videoPK', -1)

        try:
            video = Video.objects.get(pk=videoPK)
            context['video'] = video

            if request.user.is_authenticated:
                context['liked'] = VideoLike.objects.filter(user=request.user, video=video).count()
                context['watchLater'] = WatchLater.objects.filter(user=request.user, video=video).count()

                if not WatchHistory.objects.filter(user=request.user, video=video).exists():
                    WatchHistory.objects.create(user=request.user, video=video, time=datetime.datetime.now())

            comments = Comment.objects.filter(video=video).order_by('-time')

            context['comments'] = zip(comments, get_liked_comments(request.user, comments))

            titles = ['Related Videos']

            try:
                videos = video.tags.similar_objects()
            except:
                videos = []

            if videos:
                videoList = zip(videos, get_watch_later_videos(request.user, videos))
                context['videosList'] = zip(titles, [videoList])

            return render(request, 'videos/Play_Video.html', context)

        except ObjectDoesNotExist:
            return redirect('index')


########################################################################################################################
def like_video(request):
    if request.user.is_authenticated:
        videoPK = request.GET.get('videoPK', None)
        video = Video.objects.get(pk=videoPK)

        VideoLike.objects.create(user=request.user, video=video, time=datetime.datetime.now())

        return JsonResponse({'msg': 'Success'})
    else:
        return JsonResponse({'msg': 'You have to log in order to like'})


def unlike_video(request):
    if request.user.is_authenticated:
        videoPK = request.GET.get('videoPK', None)
        video = Video.objects.get(pk=videoPK)

        if VideoLike.objects.filter(user=request.user, video=video):
            VideoLike.objects.filter(user=request.user, video=video).delete()
        else:
            return JsonResponse({'msg': 'You have not liked this video yet'})

        return JsonResponse({'msg': 'Success'})
    else:
        return JsonResponse({'msg': 'You have to log in order to unlike'})


def watch_later(request):
    if request.user.is_authenticated:
        videoPK = request.GET.get('videoPK', None)
        video = Video.objects.get(pk=videoPK)

        WatchLater.objects.create(user=request.user, video=video, time=datetime.datetime.now())

        return JsonResponse({'msg': 'Success'})
    else:
        return JsonResponse({'msg': 'You have to log in order to watchLater'})


def unwatch_later(request):
    if request.user.is_authenticated:
        videoPK = request.GET.get('videoPK', None)
        video = Video.objects.get(pk=videoPK)

        if WatchLater.objects.filter(user=request.user, video=video):
            WatchLater.objects.filter(user=request.user, video=video).delete()

        return JsonResponse({'msg': 'Success'})
    else:
        return JsonResponse({'msg': 'You have to log in order to unWatchLater'})


def delete_watch_history(request):
    if request.user.is_authenticated:
        videoPK = request.GET.get('videoPK', None)
        video = Video.objects.get(pk=videoPK)

        if WatchHistory.objects.filter(user=request.user, video=video):
            WatchHistory.objects.filter(user=request.user, video=video).update(invisible=True)

        return JsonResponse({'msg': 'Success'})
    else:
        return JsonResponse({'msg': 'You have to log in order to delete history'})


def get_watch_later_videos(user, videos):
    if user.is_authenticated:
        watchLaters = []
        for video in videos:
            if WatchLater.objects.filter(user=user, video=video):
                watchLaters.append(True)
            else:
                watchLaters.append(False)
        return watchLaters
    else:
        return [False] * len(videos)


def delete_video(request):
    if request.user.is_authenticated:
        videoPK = request.GET.get('videoPK', None)

        if Video.objects.filter(pk=videoPK, user=request.user):
            video = Video.objects.get(pk=videoPK)
            if not video.isProcessed:
                return JsonResponse({'msg': 'Video is still being processed; waite a few minutes before deleting'})
            else:
                Video.objects.filter(pk=videoPK).delete()
                return JsonResponse({'msg': 'Success'})
        else:
            return JsonResponse({'msg': 'Video does not exist or you are not authorized to delete'})


def add_tags(video):
    video.tags.add(video.topic.title + "#t", video.topic.title + "@t", video.topic.title + "$t")
    video.tags.add(video.author.title + "#a", video.author.title + "@a")
    video.tags.add(video.journal.title + "#j")
    video.tags.add(video.focus.title + "#f")

    stopwords = ['what', 'which', 'is', 'are', 'have', 'has', 'that', 'of', 'a', 'the', 'those', 'not', 'dose',
                 'do', 'an', 'and', 'if', 'but', 'or', 'until', 'while', 'at', 'by', 'for', 'with', 'about',
                 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'nor',
                 'in', 'out', 'on', 'off', 'over', 'under', 'further', 'then', 'once', 'there', 'when', 'why',
                 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'against',
                 'only', 'same', 'so', 'than', 'too', 'as', 'many', 'can', 'could', 'just', 'should', 'into']

    words = video.title.split()

    for word in words:
        if word.lower() not in stopwords:
            video.tags.add(word)

    video.save()


def delete_old_videos(video):
    try:
        fs = FileSystemStorage()

        fs.delete(os.path.join(MEDIA_ROOT, 'videos/{0}'.format(os.path.basename(video.videoFile.name))))
        fs.delete(os.path.join(MEDIA_ROOT, 'videos/{0}'.format(os.path.basename(video.videoFile720.name))))
        fs.delete(os.path.join(MEDIA_ROOT, 'videos/{0}'.format(os.path.basename(video.videoFile480.name))))
        fs.delete(os.path.join(MEDIA_ROOT, 'videos/{0}'.format(os.path.basename(video.videoFile360.name))))
        fs.delete(os.path.join(MEDIA_ROOT, 'thumbnails/{0}'.format(os.path.basename(video.thumbnail.name))))
    except:
        return None


def save_video(file, random_suffix, video_suffix):
    error = False
    fs = FileSystemStorage()

    videoName = fs.save('videos/' + 'Video' + random_suffix + video_suffix, file)
    thumbnailName = 'thumbnails/' + 'Video' + random_suffix + '.png'

    try:
        clip = VideoFileClip(MEDIA_ROOT + videoName, target_resolution=(360, 480))
        clip.save_frame(MEDIA_ROOT + thumbnailName, t=random.randint(0, round(clip.duration)))

        videoFile = fs.url(videoName)
        thumbnailFile = fs.url(thumbnailName)
        duration = round(clip.duration)
    except:
        error = True
        videoFile = None
        thumbnailFile = None
        duration = -1

    return videoFile, thumbnailFile, duration, error


def start_new_thread(function):
    def decorator(*args, **kwargs):
        t = Thread(target=function, args=args, kwargs=kwargs)
        t.daemon = True
        t.start()

    return decorator


@start_new_thread
def create_different_video_qualities(video, randomSuffix, videoSuffix):
    fileName = 'Video'
    output_suffix = '.mp4'
    fs = FileSystemStorage()
    error = False

    clip = VideoFileClip(MEDIA_ROOT + 'videos/' + fileName + randomSuffix + videoSuffix,
                         target_resolution=(360, None))
    clip.write_videofile(MEDIA_ROOT + 'videos/' + fileName + randomSuffix + '_360' + output_suffix, codec='libx264',
                         temp_audiofile=MEDIA_ROOT + 'videos/temp-audio.m4a', audio_codec='aac')

    video.videoFile360 = fs.url('videos/' + fileName + randomSuffix + '_360' + output_suffix)

    clip = VideoFileClip(MEDIA_ROOT + 'videos/' + fileName + randomSuffix + videoSuffix,
                         target_resolution=(480, None))
    clip.write_videofile(MEDIA_ROOT + 'videos/' + fileName + randomSuffix + '_480' + output_suffix, codec='libx264',
                         temp_audiofile=MEDIA_ROOT + 'videos/temp-audio.m4a', audio_codec='aac')

    video.videoFile480 = fs.url('videos/' + fileName + randomSuffix + '_480' + output_suffix)

    clip = VideoFileClip(MEDIA_ROOT + 'videos/' + fileName + randomSuffix + videoSuffix,
                         target_resolution=(720, None))
    clip.write_videofile(MEDIA_ROOT + 'videos/' + fileName + randomSuffix + '_720' + output_suffix, codec='libx264',
                         temp_audiofile=MEDIA_ROOT + 'videos/temp-audio.m4a', audio_codec='aac')

    video.videoFile720 = fs.url('videos/' + fileName + randomSuffix + '_720' + output_suffix)

    video.isProcessed = True

    video.save()

    if not error:
        fs.delete(os.path.join(MEDIA_ROOT, 'videos/{0}'.format(os.path.basename(video.videoFile.name))))
