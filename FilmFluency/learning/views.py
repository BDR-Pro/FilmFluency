from django.shortcuts import render
from .models import Video, Movie

def get_videos_by_complexity(request, max_complexity):
    videos = Video.objects.filter(complexity__lte=max_complexity)
    return render(request, 'videos.html', {'videos': videos})

def get_videos_by_movie(request, slug):
    videos = Video.objects.filter(movie__random_slug=slug)
    return render(request, 'videos.html', {'videos': videos})

def get_videos_by_length(request, max_length):
    videos = Video.objects.filter(length__lte=max_length)
    return render(request, 'videos.html', {'videos': videos})

def get_unique_movies(request):
    movies = Movie.objects.distinct()
    return render(request, 'movies.html', {'movies': movies})
