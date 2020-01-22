from django.urls import path

from apps.information import views

urlpatterns = [
    path('contact/',    views.contact,  name='contact'),
    path('donate/',     views.donate,   name='donate'),
    path('about/',      views.about, name='about'),
    path('tagCloud/',   views.tag_cloud,   name='tagCloud'),
    path('terms/',      views.show_terms, name='terms'),
    path('ajax/getTags/', views.get_tags,     name='getTags'),
]
