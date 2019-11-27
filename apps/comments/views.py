import datetime

from django.http import JsonResponse

from apps.comments.models import Comment, CommentLike
from apps.videos.models import Video


def like_comment(request):
    if request.user.is_authenticated:
        commentPK = request.GET.get('commentPK', None)
        comment = Comment.objects.get(pk=commentPK)

        if not CommentLike.objects.filter(user=request.user, comment=comment).exists():
            CommentLike.objects.create(user=request.user, comment=comment, time=datetime.datetime.now())

        return JsonResponse({'msg': 'Success'})
    else:
        return JsonResponse({'msg': 'You have to log in order to like'})


def unlike_comment(request):
    if request.user.is_authenticated:
        commentPK = request.GET.get('commentPK', None)
        comment = Comment.objects.get(pk=commentPK)

        if CommentLike.objects.filter(user=request.user, comment=comment):
            CommentLike.objects.filter(user=request.user, comment=comment).delete()
        else:
            return JsonResponse({'msg': 'You have not liked this video yet'})

        return JsonResponse({'msg': 'Success'})
    else:
        return JsonResponse({'msg': 'You have to log in order to unlike'})


def delete_comment(request):
    if request.user.is_authenticated:
        commentPK = request.GET.get('commentPK', None)

        comments = Comment.objects.get(pk=commentPK).video.comments - 1

        if Comment.objects.filter(pk=commentPK):
            Comment.objects.filter(pk=commentPK).delete()

        return JsonResponse({'msg': 'Success',
                             'comments': comments})
    else:
        return JsonResponse({'msg': 'You have to log in order to delete comment'})


def post_comment(request):
    if request.user.is_authenticated:

        videoPK = request.GET.get('videoPK', None)
        text = request.GET.get('text', None)
        video = Video.objects.get(pk=videoPK)

        c = Comment.objects.create(user=request.user, video=video, parent=None, text=text, time=datetime.datetime.now())

        return JsonResponse(
            {'msg': 'Success', 'comments': video.comments, 'pk': c.pk, 'username': request.user.username})
    else:
        return JsonResponse({'msg': 'You have to log in order to unlike'})


def get_liked_comments(user, comments):
    if user.is_authenticated:
        likedComments = []
        for comment in comments:
            if CommentLike.objects.filter(user=user, comment=comment):
                likedComments.append(True)
            else:
                likedComments.append(False)
        return likedComments
    else:
        return [False] * len(comments)