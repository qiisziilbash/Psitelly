from django.core.mail import EmailMessage
from django.shortcuts import render, redirect

from apps.information.models import *
from apps.videos.models import Video


def donate(request):
    if request.method == "GET":
        context = {'newses': News.objects.order_by('-time')[:5],
                   'Statistics': True,
                   'usersCount': User.objects.filter().count(),
                   'videosCount': Video.objects.filter().count(),
                   }
        return render(request, 'information/Donate.html', context)


def contact(request):
    if request.method == "GET":
        context = {'newses': News.objects.order_by('-time')[:5],
                   'Statistics': True,
                   'usersCount': User.objects.filter().count(),
                   'videosCount': Video.objects.filter().count(),
                   }
        return render(request, 'information/Contact.html', context)
    if request.method == "POST":
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
