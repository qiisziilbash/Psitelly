from urllib.parse import urlencode
from urllib.request import urlopen
from urllib.request import Request
import json

from django.core.mail import EmailMessage
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
        ''' Begin reCAPTCHA validation '''
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

        ''' End reCAPTCHA validation '''
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
            return redirect('contact')
        else:
            context = {'newses': News.objects.order_by('-time')[:5],
                       'Statistics': True,
                       'usersCount': User.objects.filter().count(),
                       'videosCount': Video.objects.filter().count(),
                       'journalCount': Journal.objects.filter().count(),
                       'authorCount': Author.objects.filter().count(),
                       'topicCount': Topic.objects.filter().count(),
                       'focusCount': Focus.objects.filter().count(),
                       'msgs': ['Invalid reCAPTCHA. Please try again.']
                       }
            return render(request, 'information/Contact.html', context)

