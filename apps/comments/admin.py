from django.contrib import admin

from apps.comments.models import *

admin.site.register(Comment)
admin.site.register(CommentLike)
