from django.urls import path

from apps.filter import views

urlpatterns = [
    path('',        views.index,            name='index'),
    path('filter/', views.filter_videos,    name='filter'),
]