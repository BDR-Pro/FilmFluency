from django.contrib import admin

# Register your models here.

from .models import Video,Movie,Notification,Comment,Post,Community,Translation,Language,TrendingMovies

admin.site.register(Video)
admin.site.register(Movie)
admin.site.register(Notification)
admin.site.register(Comment)
admin.site.register(Post)
admin.site.register(Community)
admin.site.register(Translation)
admin.site.register(Language)
admin.site.register(TrendingMovies)