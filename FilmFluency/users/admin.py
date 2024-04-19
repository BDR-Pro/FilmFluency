from django.contrib import admin

# Register your models here.
from .models import Report,UserProgress,UserProfile


admin.site.register(Report)
admin.site.register(UserProgress)
admin.site.register(UserProfile)