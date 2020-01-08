from django.db.models import Q
from django.shortcuts import render, redirect
from django.urls import reverse
from urllib.parse import urlencode

from apps.accounts.models import Profile
from apps.information.models import News
from apps.videos.models import *
from apps.videos.views import get_watch_later_videos


def index(request):
    if request.method == "GET":
        context = {'newses': News.objects.order_by('-time')[:5],
                   'Statistics': True,
                   'usersCount': User.objects.filter().count(),
                   'videosCount': Video.objects.filter().count(),
                   'journalCount': Journal.objects.filter().count(),
                   'authorCount': Author.objects.filter().count(),
                   'topicCount': Topic.objects.filter().count(),
                   'focusCount': Focus.objects.filter().count(),
                   'isIndex': True}

        if 'search' in request.GET and request.GET.get('search', '') != '':
            keyword = request.GET.get('search', '')
            if '#' in keyword:
                return render(request, 'filter/Index.html', search_videos(context, request))
            else:
                return render(request, 'filter/Index.html', search_general(context, keyword, request.user))

        elif 'content' in request.GET and request.user.is_authenticated:
            if request.GET.get('content', '') == 'My Videos':
                videos = Video.objects.filter(user=request.user).order_by('-publishDate')

                if videos:
                    context['videosList'] = zip(['My Videos'],
                                                [zip(videos, get_watch_later_videos(request.user, videos))])
                else:
                    context['msgs'] = ['You have not uploaded any video yet']

                return render(request, 'filter/Index.html', context)

            if request.GET.get('content', '') == 'Upvoted Videos':

                likes = VideoLike.objects.filter(user=request.user)

                videos = []
                for item in likes:
                    videos.append(item.video)

                if videos:
                    context['videosList'] = zip(['Upvoted Videos'],
                                                [zip(videos, get_watch_later_videos(request.user, videos))])
                else:
                    context['msgs'] = ['You have not upvoted any video yet']

                return render(request, 'filter/Index.html', context)

            if request.GET.get('content', '') == 'Watch History':
                histories = WatchHistory.objects.filter(user=request.user, invisible=False).order_by('-time')

                videos = []
                for item in histories:
                    videos.append(item.video)

                if videos:
                    context['videosList'] = zip(['Watch History'],
                                                [zip(videos, get_watch_later_videos(request.user, videos))])
                else:
                    context['msgs'] = ['You have not any video in your watch history']

                return render(request, 'filter/Index.html', context)

            if request.GET.get('content', '') == 'Watch Later':
                watchLaters = WatchLater.objects.filter(user=request.user).order_by('-time')

                videos = []
                for item in watchLaters:
                    videos.append(item.video)

                if videos:
                    context['videosList'] = zip(['Watch Later'],
                                                [zip(videos, get_watch_later_videos(request.user, videos))])
                else:
                    context['msgs'] = ['You have not added any video to your "Watch Later" list yet']

                return render(request, 'filter/Index.html', context)

            if request.GET.get('content', '') == 'Followers':
                followings = UserFollowing.objects.filter(followee=request.user.profile).order_by('-time')

                followeeProfiles = []
                for following in followings:
                    followeeProfiles.append(following.follower)

                if followeeProfiles:
                    context['profilesTitle'] = 'Followers'
                    context['profiles'] = followeeProfiles
                else:
                    context['msgs'] = ['You have not any follower yet']

                return render(request, 'filter/Index.html', context)

            if request.GET.get('content', '') == 'Following':
                followings = UserFollowing.objects.filter(follower=request.user.profile).order_by('-time')

                followingProfiles = []
                for following in followings:
                    followingProfiles.append(following.followee)

                context['categoryTitles'] = 'Categories'
                types = []
                categories = []

                followings = FocusFollowing.objects.filter(user=request.user).order_by('-time')
                if followings:
                    for item in followings:
                        types.append('Focus')
                        categories.append(item.focus.title)

                followings = JournalFollowing.objects.filter(user=request.user).order_by('-time')
                if followings:
                    for item in followings:
                        types.append('Journal')
                        categories.append(item.journal.title)

                followings = TopicFollowing.objects.filter(user=request.user).order_by('-time')
                if followings:
                    for item in followings:
                        types.append('Topic')
                        categories.append(item.topic.title)

                followings = AuthorFollowing.objects.filter(user=request.user).order_by('-time')
                if followings:
                    for item in followings:
                        types.append('Author')
                        categories.append(item.author.title)

                msgs = []

                if categories:
                    context['categories'] = zip(types, categories)
                else:
                    msgs.append('You are not following any author, topic, focus, or journal yet')

                if followingProfiles:
                    context['profilesTitle'] = 'Users'
                    context['profiles'] = followingProfiles
                else:
                    msgs.append('You are not following any user yet')

                context['msgs'] = msgs

                return render(request, 'filter/Index.html', context)

            return render(request, 'filter/Index.html', context)

        elif 'customUser' in request.GET:
            if User.objects.filter(username=request.GET.get('customUser', '')).exists():
                user = User.objects.get(username=request.GET.get('customUser', ''))

                context['customUser'] = user

                if request.user.is_authenticated:
                    context['following'] = UserFollowing.objects.filter(follower=request.user.profile,followee=user.profile).count()
                else:
                    context['following'] = -1

                titles = ['Videos by ' + user.username]
                videos = Video.objects.filter(user=user)

                if videos:
                    videoList = zip(videos, get_watch_later_videos(request.user, videos))
                    context['videosList'] = zip(titles, [videoList])

                return render(request, 'filter/Index.html', context)

        elif 'customCategory' in request.GET:
            categoryType = request.GET.get('type', '')
            categoryName = request.GET.get('customCategory')

            if categoryType == 'Focus':
                context['customCategoryTitle'] = categoryName
                context['categoryType'] = categoryType

                if Focus.objects.filter(title=categoryName).exists():
                    focus = Focus.objects.get(title=categoryName)

                    context['customCategory'] = focus

                    if request.user.is_authenticated:
                        context['following'] = FocusFollowing.objects.filter(user=request.user, focus=focus).count()
                    else:
                        context['following'] = -1

                    titles = ['Videos by ' + categoryName + ' Focus']
                    videos = Video.objects.filter(focus=focus)

                    if videos:
                        videoList = zip(videos, get_watch_later_videos(request.user, videos))
                        context['videosList'] = zip(titles, [videoList])

                return render(request, 'filter/Index.html', context)

            elif categoryType == 'Topic':
                context['customCategoryTitle'] = categoryName
                context['categoryType'] = categoryType

                if Topic.objects.filter(title=categoryName).exists():
                    topic = Topic.objects.get(title=categoryName)

                    context['customCategory'] = topic

                    if request.user.is_authenticated:
                        context['following'] = TopicFollowing.objects.filter(user=request.user, topic=topic).count()
                    else:
                        context['following'] = -1

                    titles = ['Videos under ' + categoryName + ' Topic']
                    videos = Video.objects.filter(topic=topic)

                    if videos:
                        videoList = zip(videos, get_watch_later_videos(request.user, videos))
                        context['videosList'] = zip(titles, [videoList])

                return render(request, 'filter/Index.html', context)

            elif categoryType == 'Journal':
                context['customCategoryTitle'] = categoryName
                context['categoryType'] = categoryType

                if Journal.objects.filter(title=categoryName).exists():
                    journal = Journal.objects.get(title=categoryName)
                    context['customCategory'] = journal

                    if request.user.is_authenticated:
                        context['following'] = JournalFollowing.objects.filter(user=request.user, journal=journal).count()
                    else:
                        context['following'] = -1

                    titles = ['Videos from ' + categoryName]
                    videos = Video.objects.filter(journal=journal)

                    if videos:
                        videoList = zip(videos, get_watch_later_videos(request.user, videos))
                        context['videosList'] = zip(titles, [videoList])

                return render(request, 'filter/Index.html', context)

            elif categoryType == 'Author':
                context['customCategoryTitle'] = categoryName
                context['categoryType'] = categoryType

                if Author.objects.filter(title=categoryName).exists():
                    author = Author.objects.get(title=categoryName)
                    context['customCategory'] = author

                    if request.user.is_authenticated:
                        context['following'] = AuthorFollowing.objects.filter(user=request.user, author=author).count()
                    else:
                        context['following'] = -1

                    videos = Video.objects.filter(author=author)

                    if videos:
                        videoList = zip(videos, get_watch_later_videos(request.user, videos))
                        context['videosList'] = zip(['Videos by ' + categoryName    ], [videoList])

                return render(request, 'filter/Index.html', context)

        titles = ['Recent videos', 'Popular videos']

        recentVideos = Video.objects.order_by('-publishDate')[:4]
        popularVideos = Video.objects.order_by('-likes')[:4]

        recentVideoList = zip(recentVideos, get_watch_later_videos(request.user, recentVideos))
        popularVideoList = zip(popularVideos, get_watch_later_videos(request.user, popularVideos))

        context['videosList'] = zip(titles, [recentVideoList, popularVideoList])

        return render(request, 'filter/Index.html', context)


def filter_videos(request):
    if request.method == 'GET':
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
                   'topics': Topic.objects.all()
                   }

        return render(request, 'filter/Filter_Videos.html', context)

    if request.method == 'POST':
        title = request.POST.get('title', '')
        author = request.POST.get('author', '')
        journal = request.POST.get('journal', '')
        yearFrom = request.POST.get('yearFrom', '')
        yearTo = request.POST.get('yearTo', '')
        topic = request.POST.get('topic', '')
        focus = request.POST.get('focus', '')

        searchType = request.POST.get('searchType', 'and')

        if 'PisA' in request.POST:
            PisA = 'yes'
        else:
            PisA = 'no'

        return redirect('{}?{}'.format(reverse('index'), urlencode({'search': '#',
                                                                    'title': title,
                                                                    'author': author,
                                                                    'yearFrom': yearFrom,
                                                                    'yearTo': yearTo,
                                                                    'journal': journal,
                                                                    'topic': topic,
                                                                    'focus': focus,
                                                                    'searchType': searchType,
                                                                    'PisA': PisA})))


def search_videos(context, request):
    try:
        titles = ['Filtered Videos']

        title = request.GET.get('title', '')
        author = request.GET.get('author', '')
        journal = request.GET.get('journal', '')
        yearFrom = request.GET.get('yearFrom', '')
        yearTo = request.GET.get('yearTo', '')
        topic = request.GET.get('topic', '')
        focus = request.GET.get('focus', '')
        searchType = request.GET.get('searchType', '')
        PisA = request.GET.get('PisA', '')

        if searchType == 'and':
            if title + author + yearTo + yearFrom + journal + topic + focus == '':
                videos = Video.objects.none()
            else:
                if title != '':
                    videos = Video.objects.filter(title__icontains=title)
                else:
                    videos = Video.objects.all()
                if author != '':
                    videos = videos.filter(author__name__icontains=author)
                if journal != '':
                    videos = videos.filter(journal__name__icontains=journal)
                if yearFrom != '':
                    videos = videos.filter(year__gte=yearFrom)
                if yearTo != '':
                    videos = videos.filter(year__lte=yearTo)
                if topic != '':
                    videos = videos.filter(topic__text__icontains=topic)
                if focus != '':
                    videos = videos.filter(focus__text__icontains=focus)
        else:
            if title != '':
                videos = Video.objects.filter(title__icontains=title)
            else:
                videos = Video.objects.none()
            if author != '':
                videos = videos | Video.objects.filter(author__name__icontains=author)
            if journal != '':
                videos = videos | Video.objects.filter(journal__name__icontains=journal)
            if yearFrom != '':
                videos = videos | Video.objects.filter(year__gte=yearFrom)
            if yearTo != '':
                videos = videos | Video.objects.filter(year__lte=yearTo)
            if topic != '':
                videos = videos | Video.objects.filter(topic__text__icontains=topic)
            if focus != '':
                videos = videos | Video.objects.filter(focus__text__icontains=focus)
    except:
        titles = ['Search query was not in a right format']
        videos = Video.objects.none()

    if videos:
        videoList = zip(videos, get_watch_later_videos(request.user, videos))
        context['videosList'] = zip(titles, [videoList])
    else:
        context['msgs'] = ['No videos found for the criteria specified in the filter section']

    return context


def search_general(context, keyword, user):
    msgs = []

    # Users
    profiles = Profile.objects.filter(user__username__icontains=keyword).filter(~Q(user__username=user.username))
    if profiles:
        context['profilesTitle'] = 'Users'
        context['profiles'] = profiles
    else:
        msgs.append('No users found for the query')

    # Categories
    types = []
    categories = []

    focuses = Focus.objects.filter(title__icontains=keyword)
    if focuses:
        for focus in focuses:
            types.append('Focus')
            categories.append(focus.title)

    journals = Journal.objects.filter(title__icontains=keyword)
    if journals:
        for journal in journals:
            types.append('Journal')
            categories.append(journal.title)

    topics = Topic.objects.filter(title__icontains=keyword)
    if topics:
        for topic in topics:
            types.append('Topic')
            categories.append(topic.title)

    authors = Author.objects.filter(title__icontains=keyword)
    if authors:
        for author in authors:
            types.append('Author')
            categories.append(author.title)

    if categories:
        context['categoryTitles'] = 'Categories'
        context['categories'] = zip(types, categories)
    else:
        msgs.append('No categories found for the query')

    # videos
    videos = Video.objects.filter(title__icontains=keyword)

    if videos:
        titles = ['Videos']
        videoList = zip(videos, get_watch_later_videos(user, videos))
        context['videosList'] = zip(titles, [videoList])
    else:
        msgs.append('No videos found for the query')

    if msgs:
        context['msgs'] = msgs

    return context

