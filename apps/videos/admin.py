from django.contrib import admin

from apps.videos.models import *

admin.site.register(Video)

admin.site.register(Focus)
admin.site.register(FocusFollowing)

admin.site.register(Topic)
admin.site.register(TopicFollowing)

admin.site.register(Journal)
admin.site.register(JournalFollowing)

admin.site.register(Author)
admin.site.register(AuthorFollowing)

admin.site.register(VideoLike)
admin.site.register(WatchHistory)
admin.site.register(WatchLater)