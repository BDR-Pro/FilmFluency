# FilmFluency/urls.py
from django.urls import path
from learning import views

app_name = 'learning'

urlpatterns = [
    path('complexity/', views.get_videos_by_complexity, name='videos_by_complexity'),
    path('movie/<str:random_slug>/', views.get_videos_by_movie, name='videos_by_movie'),
    path('length/<int:max_length>/', views.get_videos_by_length, name='videos_by_length'),
    path('movies/', views.get_unique_movies, name='unique_movies'),
]
