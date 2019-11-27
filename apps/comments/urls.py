from django.urls import path

from apps.comments import views

urlpatterns = [

    path('ajax/deleteComment/',     views.delete_comment,   name='deleteComment'),

    path('ajax/likeComment/',       views.like_comment,     name='likeComment'),
    path('ajax/unlikeComment/',     views.unlike_comment,   name='unlikeComment'),

    path('ajax/comment/',           views.post_comment,     name='comment'),
]