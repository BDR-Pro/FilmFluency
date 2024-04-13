# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('videos/', views.video_list, name='video_list'),
    path('videos/<int:video_id>/', views.video_detail, name='video_detail'),
]
