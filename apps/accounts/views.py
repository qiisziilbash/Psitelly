from urllib.parse import urlencode
from urllib.request import urlopen
from urllib.request import Request
import json

import random
import re

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
                    request.user.save()
                    msgs.append('Your username is updated')
                else:
                    msgs.append('Entered username already exists; pick another username')

            if not email == request.user.email:
                if not User.objects.filter(email=email).exists():
                    request.user.email = email
                    request.user.profile.emailVerified = False
                    request.user.save()
                    msgs.append('Your email is updated')
                    context['verify'] = True
                else:
                    msgs.append('Entered email address already exists; pick another email')

            if not newPass1 == '':
                if len(newPass1) > 2:
                    if newPass1 == newPass2:
                        request.user.set_password(newPass1)
                        request.user.save()
                        user = authenticate(username=username, password=newPass1)
                        login(request, user)
                        msgs.append('Your password is updated')
                    else:
                        msgs.append('Entered passwords do not match')
                else:
                    msgs.append('Password format is invalid. Password should have at least 1 digit, 1 uppercase and' +
                                '1 lowercase character ')

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
                msgs.append('Your notification settings is updated.')

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
        followType = request.GET.get('followType', '')
        customCategory = request.GET.get('customCategory', '')

        if followType == 'user':
            followee = User.objects.get(username=request.GET.get('username', ''))
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

        followType = request.GET.get('followType', '')
        customCategory = request.GET.get('customCategory', '')

        if followType == 'user':
            followee = User.objects.get(username=request.GET.get('username', ''))
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
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        if User.objects.filter(username_iexact=username).exists() or User.objects.filter(email_iexact=username):
            if User.objects.filter(username_iexact=username).exists():
                user = User.objects.get(username_iexact=username)
            else:
                user = User.objects.get(email_iexact=username)

            username = user.username

            if user.profile.emailVerified:
                user = authenticate(username=username, password=password)
                if user:
                    login(request, user)
                    return redirect('index')
                else:
                    msg = 'Password is not correct'
            else:
                msg = 'Your email is not verified'
        else:
            msg = 'This username or email does not exist in our database'

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
        try:
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
                username = request.POST.get('username', '')
                email = request.POST.get('email', '')

                if not User.objects.filter(username__iexact=username).exists():
                    if not User.objects.filter(email_iexact=email).exists():
                        try:
                            password = request.POST.get('password', '')
                            if len(password) > 2:
                                password = make_password(password)
                            else:
                                return JsonResponse({'msg': 'Password format is invalid'})

                            user = User.objects.create(username=username, email=email, password=password)

                            user.profile.notifyComments = True
                            user.profile.notifyFollows = True
                            user.profile.notifyUploads = True
                            user.profile.notifyMentions = True
                            user.profile.emailComments = True
                            user.profile.emailUploads = True
                            user.profile.emailFollows = True
                            user.profile.emailMentions = True
                            user.profile.save()

                            send_code(user, 'verifyEmail')

                            return JsonResponse({'msg': 'Success'})
                        except:
                            User.objects.get(username=username).delete()
                            return JsonResponse({'msg': 'Registration failed probably due to an invalid email address'})
                    else:
                        return JsonResponse({'msg': 'This email is already used'})
                else:
                    return JsonResponse({'msg': 'This username is already picked'})
            else:
                return JsonResponse({'msg': 'Invalid reCAPTCHA. Please try again.'})
        except:
            return JsonResponse({'msg': 'reChaptcha evaluation failed.'})


def post_register(request):
    if request.method == "POST":
        username = request.POST.get('username', '')
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')

        if User.objects.filter(username=username, email=email).exists():
            user = User.objects.get(username=username, email=email)
            code = request.POST.get('code', '')

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
            password = request.POST.get('newPassword', '')
            code = request.POST.get('code', '')

            codeRequestTime = user.profile.codeRequestTime.replace(tzinfo=utc)

            now = datetime.datetime.now().replace(tzinfo=utc)

            if not codeRequestTime + datetime.timedelta(minutes=5) < now:

                if len(password) > 2:
                    if str(user.profile.code) == code:
                        user.set_password(password)
                        user.save()

                        user = authenticate(username=user.username, password=password)

                        if user:
                            login(request, user)
                            return JsonResponse({'msg': 'Success'})
                        else:
                            return JsonResponse({'msg': 'Password change failed'})
                    else:
                        return JsonResponse({'msg': 'Entered code is not correct; please try again'})
                else:
                    return JsonResponse({'msg': 'Entered password does not follow the specified format'})

            else:
                try:
                    send_code(user, 'passwordChange')
                    return JsonResponse(
                        {'msg': 'Entered code is expired; another code has been sent. Check your email again.'})
                except:
                    return JsonResponse(
                        {'msg': 'Entered code is expired. Contact us for more detail.'})
        else:
            return JsonResponse({'msg': 'This email does not exist in our database'})


def send_verification_code(request):
    if request.method == "POST":
        email = request.POST.get('email', '')
        type = request.POST.get('type', '')

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)

            if type == 'emailVerification':
                if not user.profile.emailVerified:
                    try:
                        send_code(user, type)
                        return JsonResponse({'msg': 'Success'})
                    except:
                        return JsonResponse({'msg': 'Sending email to this address failed; please try again'})
                else:
                    return JsonResponse({'msg': 'This email is already verified'})
            elif type == 'passwordChange':
                try:
                    send_code(user, type)
                    return JsonResponse({'msg': 'Success'})
                except:
                    return JsonResponse({'msg': 'Sending email to this address failed; please try again'})
            else:
                return JsonResponse({'msg': 'Verification type is not identified'})
        else:
            return JsonResponse({'msg': 'This email does not exist in our database'})


def verify_code(request):
    if request.method == "POST":
        email = request.POST.get('email', '')

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)

            codeRequestTime = user.profile.codeRequestTime.replace(tzinfo=utc)
            now = datetime.datetime.now().replace(tzinfo=utc)

            if not codeRequestTime + datetime.timedelta(minutes=5) < now:

                if str(user.profile.code) == request.POST.get('code', ''):
                    user.profile.emailVerified = True
                    user.save()

                    return JsonResponse({'msg': 'Success'})
                else:
                    return JsonResponse({'msg': 'Entered code is not correct; please try again'})
            else:
                try:
                    send_code(user, 'emailVerification')
                    return JsonResponse(
                        {'msg': 'Entered code is expired; another code has been sent. Check your email again.'})
                except:
                    return JsonResponse(
                        {'msg': 'Entered code is expired. Contact us for more detail.'})
        else:
            return JsonResponse({'msg': 'This email does not exist in our database'})


########################################################################################################################
def send_code(user, type):
    user.profile.code = random.randint(10000, 10000000)
    user.profile.codeRequestTime = datetime.datetime.now()

    if type == 'emailVerification':
        user.profile.emailVerified = False

    user.save()

    subject = 'Verification code for Psitelly'
    msg = 'Dear %s\n\nYou are receiving this email because your email address is used to verify an account ' \
          'in psitelly.com.' \
          '\nThis is your verification code: %d\n\nThanks,\n Psitelly' % (
              user.username, user.profile.code)

    send_mail(subject, msg, 'psitelly@gmail.com', [user.email], fail_silently=True)

    return 0


def purge_file(directory, pattern):
    for f in os.listdir(directory):
        if re.search(pattern, f):
            os.remove(os.path.join(directory, f))

