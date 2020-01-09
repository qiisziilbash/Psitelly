from urllib.parse import urlencode
from urllib.request import urlopen
from urllib.request import Request
import json

from django.core.mail import EmailMessage
from django.http import JsonResponse
from django.shortcuts import render, redirect

from Psitelly import settings
from apps.information.models import *
from apps.videos.models import Video, Journal, Author, Topic, Focus


def donate(request):
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
        return render(request, 'information/Donate.html', context)


def tag_cloud(request):
    if request.method == "GET":
        context = {'newses': News.objects.order_by('-time')[:5],
                   'Statistics': True,
                   'usersCount': User.objects.filter().count(),
                   'videosCount': Video.objects.filter().count(),
                   'journalCount': Journal.objects.filter().count(),
                   'authorCount': Author.objects.filter().count(),
                   'topicCount': Topic.objects.filter().count(),
                   'focusCount': Focus.objects.filter().count(),
                   'tag_cloud_type': request.GET.get('type', 'general')
                   }

        return render(request, 'information/Tag_Cloud.html', context)


def show_terms(request):
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

        return render(request, 'information/Terms.html', context)


def get_tags(request):
    type = request.GET.get('type', 'general')
    tags_dict = {}
    tags = []
    videos = Video.objects.all()

    if type == 'authors':
        for video in videos:
            for tag in video.tags.all():
                if tag.name[-2:] == '#a' or tag.name[-2:] == '@a':
                    tag_name = tag.name[0:-2]
                    if tag_name in tags_dict:
                        tags_dict[tag_name] = tags_dict[tag_name] + 1
                    else:
                        tags_dict[tag_name] = 1
                    break
    elif type == 'journals':
        for video in videos:
            for tag in video.tags.all():
                if tag.name[-2:] == '#j':
                    tag_name = tag.name[0:-2]
                    if tag_name in tags_dict:
                        tags_dict[tag_name] = tags_dict[tag_name] + 1
                    else:
                        tags_dict[tag_name] = 1

    elif type == 'focuses':
        for video in videos:
            for tag in video.tags.all():
                if tag.name[-2:] == '#f':
                    tag_name = tag.name[0:-2]
                    if tag_name in tags_dict:
                        tags_dict[tag_name] = tags_dict[tag_name] + 1
                    else:
                        tags_dict[tag_name] = 1
    elif type == 'topics':
        for video in videos:
            for tag in video.tags.all():
                if tag.name[-2:] == '#t' or tag.name[-2:] == '@t' or tag.name[-2:] == '$t':
                    tag_name = tag.name[0:-2]
                    if tag_name in tags_dict:
                        tags_dict[tag_name] = tags_dict[tag_name] + 1
                    else:
                        tags_dict[tag_name] = 1
                    break
    else:
        for video in videos:
            for tag in video.tags.all():
                if tag.name[-2] == '@' or tag.name[-2] == '#' or tag.name[-2] == '$':
                    tag_name = tag.name[0:-2]
                else:
                    tag_name = tag.name
                if tag_name in tags_dict:
                    tags_dict[tag_name] = tags_dict[tag_name] + 1
                else:
                    tags_dict[tag_name] = 1

    for tag in tags_dict:
        tags.append({"tag": tag, 'count': tags_dict[tag]})

    tags.append({'tag': 'ahmad', 'count': 10})

    return JsonResponse(tags, safe=False)


def contact(request):
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
        return render(request, 'information/Contact.html', context)
    if request.method == "POST":

        context = {'newses': News.objects.order_by('-time')[:5],
                   'Statistics': True,
                   'usersCount': User.objects.filter().count(),
                   'videosCount': Video.objects.filter().count(),
                   'journalCount': Journal.objects.filter().count(),
                   'authorCount': Author.objects.filter().count(),
                   'topicCount': Topic.objects.filter().count(),
                   'focusCount': Focus.objects.filter().count(),
                   'msgs': []
                   }

        recaptcha_response = request.POST.get('g-recaptcha-response')
        url = 'https://www.google.com/recaptcha/api/siteverify'
        values = {
            'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response
        }

        data = urlencode(values).encode("utf-8")
        req = Request(url, data)
        response = urlopen(req)
        result = json.load(response)

        if result['success']:
            content = request.POST.get('content', '')
            email = request.POST.get('email', '')
            subject = request.POST.get('subject', '')
            msg = EmailMessage(subject, content, 'psitelly@gmail.com', ['mshafiei0423@gmail.com'], reply_to=[email])

            if 'picture1' in request.FILES:
                picture1 = request.FILES['picture1']
                msg.attach(picture1.name, picture1.read(), picture1.content_type)
            if 'picture2' in request.FILES:
                picture2 = request.FILES['picture2']
                msg.attach(picture2.name, picture2.read(), picture2.content_type)
            if 'picture3' in request.FILES:
                picture3 = request.FILES['picture3']
                msg.attach(picture3.name, picture3.read(), picture3.content_type)

            msg.send()
            context['msgs'].append('Thank you. We received your feedback.')
            return render(request, 'information/Contact.html', context)
        else:
            context['msgs'].append('Invalid reCAPTCHA. Please try again.')
            return render(request, 'information/Contact.html', context)

