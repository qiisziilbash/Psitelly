from urllib.parse import urlencode
from urllib.request import urlopen
from urllib.request import Request
import json

import random
import re
import string

from pytz import utc

from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.shortcuts import render, redirect

from Psitelly import settings
from apps.information.models import News
from apps.videos.models import *


def show_profile(request):
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
        if 'logout' in request.GET:
            logout(request)
            return redirect('index')
        elif 'edit' in request.GET:
            return redirect('editProfile')
        else:
            return render(request, 'accounts/Profile.html', context)


def edit_profile(request):
    context = {'newses': News.objects.order_by('-time')[:5],
               'Statistics': True,
               'usersCount': User.objects.filter().count(),
               'videosCount': Video.objects.filter().count(),
               'journalCount': Journal.objects.filter().count(),
               'authorCount': Author.objects.filter().count(),
               'topicCount': Topic.objects.filter().count(),
               'focusCount': Focus.objects.filter().count(),
               }

    if request.method == "GET":
        return render(request, 'accounts/Edit_Profile.html', context)

    if request.method == "POST":
        if 'cancel' in request.POST:
            return redirect('profile')

        if 'save' in request.POST:
            msgs =[]

            username = request.POST.get('username', '')
            email = request.POST.get('email', '')

            secQuestion = request.POST.get('secQuestion', '')
            secAnswer = request.POST.get('secAnswer', '')

            newPass1 = request.POST.get('newPass1', '')
            newPass2 = request.POST.get('newPass2', '')

            if 'profilePicture' in request.FILES:
                profilePicture = request.FILES['profilePicture']

                purge_file(os.path.join(MEDIA_ROOT, 'profiles/'), request.user.username + ".*")

                fs = FileSystemStorage()
                filename = fs.save('profiles/' + request.user.username + os.path.splitext(profilePicture.name)[1],
                                   profilePicture)

                request.user.profile.picture = fs.url(filename)

            if not username == request.user.username:
                if not User.objects.filter(username=username).exists():
                    request.user.username = username
                    msgs.append('Your username is updated')
                else:
                    msgs.append('Entered username already exists; pick another username')

            if not email == request.user.email:
                if not User.objects.filter(email=email).exists():
                    request.user.email = email
                    msgs.append('Your email is updated')
                else:
                    msgs.append('Entered email address already exists; pick another email')

            if not request.user.profile.secQuestion == secQuestion:
                request.user.profile.secQuestion = secQuestion
                msgs.append('Your security question is updated')

            if not request.user.profile.secAnswer == secAnswer:
                request.user.profile.secAnswer = secAnswer
                msgs.append('Your security Answer is updated')

            if not newPass1 == '':
                if newPass1 == newPass2:
                    request.user.set_password(newPass1)
                    user = authenticate(username=username, password=newPass1)
                    login(request, user)
                    msgs.append('Your password is updated')
                else:
                    msgs.append('Entered passwords do not match')

            notificationsIsUpdated = False

            notifyUploads = True if 'notifyUploads' in request.POST else False
            emailUploads = True if 'emailUploads' in request.POST else False

            notifyComments = True if 'notifyComments' in request.POST else False
            emailComments = True if 'emailComments' in request.POST else False

            notifyFollows = True if 'notifyFollows' in request.POST else False
            emailFollows = True if 'emailFollows' in request.POST else False

            notifyMentions = True if 'notifyMentions' in request.POST else False
            emailMentions = True if 'emailMentions' in request.POST else False

            if not notifyUploads == request.user.profile.notifyUploads:
                request.user.profile.notifyUploads = notifyUploads
                notificationsIsUpdated = True

            if not emailUploads == request.user.profile.emailUploads:
                request.user.profile.emailUploads = emailUploads
                notificationsIsUpdated = True

            if not notifyComments == request.user.profile.notifyComments:
                request.user.profile.notifyComments = notifyComments
                notificationsIsUpdated = True

            if not emailComments == request.user.profile.emailComments:
                request.user.profile.emailComments = emailComments
                notificationsIsUpdated = True

            if not notifyFollows == request.user.profile.notifyFollows:
                request.user.profile.notifyFollows = notifyFollows
                notificationsIsUpdated = True

            if not emailFollows == request.user.profile.emailFollows:
                request.user.profile.emailFollows = emailFollows
                notificationsIsUpdated = True

            if not notifyMentions == request.user.profile.notifyMentions:
                request.user.profile.notifyMentions = notifyMentions
                notificationsIsUpdated = True

            if not emailMentions == request.user.profile.emailMentions:
                request.user.profile.emailMentions = emailMentions
                notificationsIsUpdated = True

            if notificationsIsUpdated:
                msgs.append('Your notification setting is updated.')

            request.user.save()
            request.user.profile.save()

            if msgs:
                context['msgs'] = msgs

        return render(request, 'accounts/Edit_Profile.html', context)


def show_notifications(request):
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

        notifications = Notification.objects.filter(user=request.user).order_by('-time')

        if notifications:
            context['notificaations'] = notifications
        else:
            msgs = ["You don't have any notifications"]
            context['msgs'] = msgs

        return render(request, 'accounts/Notification.html', context)


def clear_notifications(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            request.user.profile.hasNotifications = False
            request.user.profile.save()

            Notification.objects.filter(user=request.user, seen=False).update(seen=True)

            return JsonResponse({'msg': 'Success'})
        else:
            return JsonResponse({'msg': 'You are not logged in yet'})

    else:
        return JsonResponse({'msg': 'This  request failed, my dear!'})


def delete_notifications(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            notificationPK = request.GET.get('notificationPK', -1)

            if Notification.objects.filter(pk=notificationPK).exists():
                Notification.objects.get(pk=notificationPK).delete()

            return JsonResponse({'msg': 'Success'})
        else:
            return JsonResponse({'msg': 'You are not logged in yet'})

    else:
        return JsonResponse({'msg': 'This  request failed, my dear!'})


def follow(request):
    if request.user.is_authenticated:
        followType = request.GET.get('followType', None)
        customCategory = request.GET.get('customCategory', None)

        if followType == 'user':
            followee = User.objects.get(username=request.GET.get('username', None))
            UserFollowing.objects.create(follower=request.user.profile, followee=followee.profile)

        elif followType == 'Focus':
            focus = Focus.objects.get(title=customCategory)
            FocusFollowing.objects.create(user=request.user, focus=focus, time=datetime.datetime.now())

        elif followType == 'Journal':
            journal = Journal.objects.get(title=customCategory)
            JournalFollowing.objects.create(user=request.user, journal=journal, time=datetime.datetime.now())

        elif followType == 'Topic':
            topic = Topic.objects.get(title=customCategory)
            TopicFollowing.objects.create(user=request.user, topic=topic, time=datetime.datetime.now())

        elif followType == 'Author':
            author = Author.objects.get(title=customCategory)
            AuthorFollowing.objects.create(user=request.user, author=author, time=datetime.datetime.now())

        return JsonResponse({'msg': 'Success'})
    else:
        return JsonResponse({'msg': 'You need to log in to follow'})


def unfollow(request):
    if request.user.is_authenticated:

        followType = request.GET.get('followType', None)
        customCategory = request.GET.get('customCategory', None)

        if followType == 'user':
            followee = User.objects.get(username=request.GET.get('username', None))
            UserFollowing.objects.get(follower=request.user.profile, followee=followee.profile).delete()

        elif followType == 'Focus':
            focus = Focus.objects.get(title=customCategory)
            FocusFollowing.objects.get(user=request.user, focus=focus).delete()

        elif followType == 'Journal':
            journal = Journal.objects.get(title=customCategory)
            JournalFollowing.objects.get(user=request.user, journal=journal).delete()

        elif followType == 'Topic':
            topic = Topic.objects.get(title=customCategory)
            TopicFollowing.objects.get(user=request.user, topic=topic).delete()

        elif followType == 'Author':
            author = Author.objects.get(title=customCategory)
            AuthorFollowing.objects.get(user=request.user, author=author).delete()

        return JsonResponse({'msg': 'Success'})
    else:
        return JsonResponse({'msg': 'You need to log in to unFollow'})


########################################################################################################################
def sign_in(request):
    context = {'newses': News.objects.order_by('-time')[:5],
               'Statistics': True,
               'usersCount': User.objects.filter().count(),
               'videosCount': Video.objects.filter().count(),
               'journalCount': Journal.objects.filter().count(),
               'authorCount': Author.objects.filter().count(),
               'topicCount': Topic.objects.filter().count(),
               'focusCount': Focus.objects.filter().count(),
               }

    if request.method == "GET":
        return render(request, 'accounts/Login.html', context)

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        if User.objects.filter(username=username).exists():
            user = authenticate(username=username, password=password)
            if user:
                if user.profile.emailVerified:
                    login(request, user)
                    return redirect('index')
                else:
                    msg = 'Your email is not verified'
            else:
                msg = 'Password is not correct'
        else:
            msg = 'This username does not exist'

        context['msgs'] = [msg]

        return render(request, 'accounts/Login.html', context)


def register(request):
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
        return render(request, 'accounts/Register.html', context)


def verify_account(request):
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
        return render(request, 'accounts/Verify_Account.html', context)


def forgot(request):
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
        return render(request, 'accounts/Forgot_Password.html', context)


########################################################################################################################
def pre_register(request):
    if request.method == "POST":

        url = 'https://www.google.com/recaptcha/api/siteverify'
        values = {
            'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
            'response': request.POST.get('recaptcha', None)
        }

        data = urlencode(values).encode("utf-8")
        req = Request(url, data)
        response = urlopen(req)
        result = json.load(response)

        if result['success']:
            username = request.POST.get('username', None)
            email = request.POST.get('email', None)

            if not User.objects.filter(username=username).exists():
                if not User.objects.filter(email=email).exists():
                    try:
                        password = make_password(request.POST.get('password', None))
                        secQuestion = request.POST.get('secQuestion', None)
                        secAnswer = request.POST.get('secAnswer', None)

                        user = User.objects.create(username=username, email=email, password=password)
                        user.profile.secAnswer = secAnswer
                        user.profile.secQuestion = secQuestion
                        user.profile.save()

                        send_code(user)

                        return JsonResponse({'msg': 'Success'})
                    except:
                        return JsonResponse({'msg': 'We could not register this account since entered email is not valid'})
                else:
                    return JsonResponse({'msg': 'This email is already used'})
            else:
                return JsonResponse({'msg': 'This username is already picked'})
        else:
            return JsonResponse({'msg': 'Invalid reCAPTCHA. Please try again.'})


def post_register(request):
    if request.method == "POST":
        username = request.POST.get('username', None)
        email = request.POST.get('email', None)
        password = request.POST.get('password', None)

        if User.objects.filter(username=username, email=email).exists():
            user = User.objects.get(username=username, email=email)
            code = request.POST.get('code', None)

            codeRequestTime = user.profile.codeRequestTime.replace(tzinfo=utc)
            now = datetime.datetime.now().replace(tzinfo=utc)

            if not codeRequestTime + datetime.timedelta(minutes=5) < now:

                if str(user.profile.code) == code:
                    user.profile.emailVerified = True
                    user.save()

                    user = authenticate(username=user, password=password)
                    login(request, user)

                    return JsonResponse({'msg': 'Success'})
                else:
                    return JsonResponse({'msg': 'Entered code is not correct; please try again'})

            else:
                try:
                    send_code(user)
                    return JsonResponse(
                        {'msg': 'Entered code is expired; another code has been sent. Check your email again.'})
                except:
                    return JsonResponse(
                        {'msg': 'Entered code is expired. Contact us for more detail.'})
        else:
            return JsonResponse({'msg': 'This user does not exist in our database'})


def change_password(request):
    if request.method == "POST":
        email = request.POST.get('email', None)

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            secQuestion = request.POST.get('secQuestion', None)
            secAnswer = request.POST.get('secAnswer', None)

            if user.profile.secQuestion == secQuestion and user.profile.secAnswer == secAnswer:
                try:
                    send_password(user)
                    return JsonResponse({'msg': 'Success'})
                except:
                    return JsonResponse({'msg': 'We could not send password since entered email is not valid'})
            else:
                return JsonResponse({'msg': 'Your security question or answer does not match the records'})

        else:
            return JsonResponse({'msg': 'This email does not exist in our database'})


def send_verification_code(request):
    if request.method == "POST":
        email = request.POST.get('email', None)

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=request.POST.get('email', None))
            secQuestion = request.POST.get('secQuestion', None)
            secAnswer = request.POST.get('secAnswer', None)

            if user.profile.secQuestion == secQuestion and user.profile.secAnswer == secAnswer:
                if not user.profile.emailVerified:
                    try:
                        send_code(user)
                        return JsonResponse({'msg': 'Success'})
                    except:
                        return JsonResponse({'msg': 'We could not verify your account since your email is not valid.'})
                else:
                    return JsonResponse({'msg': 'This email is already verified'})
            else:
                return JsonResponse({'msg': 'Your security question or answer does not match the records'})
        else:
            return JsonResponse({'msg': 'This email does not exist in our database'})


def verify_code(request):
    if request.method == "POST":
        email = request.POST.get('email', None)

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)

            codeRequestTime = user.profile.codeRequestTime.replace(tzinfo=utc)
            now = datetime.datetime.now().replace(tzinfo=utc)

            if not codeRequestTime + datetime.timedelta(minutes=5) < now:

                if str(user.profile.code) == request.POST.get('code', None):
                    user.profile.emailVerified = True
                    user.save()

                    return JsonResponse({'msg': 'Success'})
                else:
                    return JsonResponse({'msg': 'Entered code is not correct; please try again'})
            else:
                try:
                    send_code(user)
                    return JsonResponse(
                        {'msg': 'Entered code is expired; another code has been sent. Check your email again.'})
                except:
                    return JsonResponse(
                        {'msg': 'Entered code is expired. Contact us for more detail.'})
        else:
            return JsonResponse({'msg': 'This email does not exist in our database'})


########################################################################################################################
def send_code(user):
    user.profile.code = random.randint(1, 1000000)
    user.profile.codeRequestTime = datetime.datetime.now()
    user.profile.emailVerified = False

    user.save()

    subject = 'Confirmation code for Psitelly Registration'
    msg = 'Dear %s\n\nYou are receiving this email because your email address is used to register in psitelly.com.' \
          '\nThis is your confirmation code for registration: %d\n\nThanks,\n Psitelly' % (
              user.username, user.profile.code)

    send_mail(subject, msg, 'psitelly@gmail.com', [user.email], fail_silently=True)

    return 0


def send_password(user):
    newPassword = generate_password(12)
    user.set_password(newPassword)
    user.save()

    subject = 'New Password for Psitelly Account'
    msg = 'Dear %s\n\nYou are receiving this email because your email address is used to reset password in ' \
          'psitelly.com.' \
          '\nThis is your new password: %s\n Please delete this email after reading for the security purposes.\n\n ' \
          'Thanks,\n Psitelly' % (user.username, newPassword)

    send_mail(subject, msg, 'psitelly@gmail.com', [user.email], fail_silently=True)
    return 0


def generate_password(size, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def purge_file(directory, pattern):
    for f in os.listdir(directory):
        if re.search(pattern, f):
            os.remove(os.path.join(directory, f))

