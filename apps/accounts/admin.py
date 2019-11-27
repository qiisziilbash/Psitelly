from django.contrib import admin
from apps.accounts.models import *

admin.site.register(Profile)
admin.site.register(UserFollowing)
admin.site.register(Notification)
