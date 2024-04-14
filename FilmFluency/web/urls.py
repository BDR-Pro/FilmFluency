# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('all/', views.video_list, name='video_list'),
    path('detail/<str:slug>/', views.video_detail, name='video_detail'),
]
