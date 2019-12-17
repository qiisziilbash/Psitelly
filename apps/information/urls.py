from django.urls import path

from apps.information import views

urlpatterns = [
    path('contact/',    views.contact,  name='contact'),
    path('donate/',     views.donate,   name='donate'),
    path('tagCloud/',     views.tag_cloud,   name='tagCloud'),
    path('ajax/getTags/', views.get_tags,     name='getTags'),
]
