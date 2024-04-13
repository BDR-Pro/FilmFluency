from .models import Video
from django.shortcuts import render


def get_videos_by_complexity(request, max_complexity):
    videos = Video.objects.filter(complexity__lte=max_complexity)
    return render(request, 'videos.html', {'videos': videos})

def get_videos_by_movie(request, movie_name):
    videos = Video.objects.filter(movie__icontains=movie_name)
    return render(request, 'videos.html', {'videos': videos})


def get_videos_by_length(request, max_length):
    videos = Video.objects.filter(length__lte=max_length)
    return render(request, 'videos.html', {'videos': videos})


def get_unique_movies(request):
    movies = Video.objects.values_list('movie', flat=True).distinct()
    return render(request, 'videos.html', {'videos': movies})

