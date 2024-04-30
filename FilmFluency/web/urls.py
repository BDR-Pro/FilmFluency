# urls.py
from django.urls import path
from . import views

app_name = "web"

urlpatterns = [
    path('', views.home, name='home'),
    path('all/', views.video_list, name='video_list'),
    path('detail/<str:random_slug>/', views.video_detail, name='video_detail'),
    path('movie/<str:random_slug>/', views.get_movie_by_slug, name='movie_detail'),
    path('random/', views.random_movie, name='random'),
    path('search/', views.search_movies, name='search_movies'),
    path('dashboard', views.dashboard_view, name='dashboard'),
    path('posters/<str:random_slug>/', views.get_posters, name='posters'),
]