from django.urls import path

from apps.videos import views

urlpatterns = [
    path('upload/',             views.upload_video,         name='upload'),
    path('editVideo/',          views.edit_video,           name='editVideo'),
    path('playVideo/',          views.play_video,           name='playVideo'),

    path('ajax/like/',          views.like_video,           name='like'),
    path('ajax/unlike/',        views.unlike_video,         name='unlike'),

    path('ajax/watchLater/',    views.watch_later,          name='watchLater'),
    path('ajax/unWatchLater/',  views.unwatch_later,        name='unWatchLater'),

    path('ajax/deleteHistory/', views.delete_watch_history, name='deleteHistory'),
]
