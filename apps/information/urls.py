from django.urls import path

from apps.information import views

urlpatterns = [
    path('contact/',    views.contact,  name='contact'),
    path('donate/',     views.donate,   name='donate'),
]
