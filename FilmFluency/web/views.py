from django.shortcuts import render, get_object_or_404
from django.db.models import F
from learning.models import Video, TrendingMovies

def get_all_videos():
    """ Return all videos in the database. """
    return Video.objects.all()

def get_video_by_slug(slug):
    """ Return a specific video by its unique slug. """
    video = get_object_or_404(Video, random_slug=slug)
    # Increment views for the movie associated with the video
    TrendingMovies.objects.filter(title=video.movie.title).update(views=F('views') + 1)
    return video

def get_trending_movies():
    """ Return top 5 trending movies based on views. """
    return TrendingMovies.objects.order_by('-views')[:5]

def home(request):
    """ Render the homepage with introductory information and top trending movies. """
    movies = get_trending_movies()
    return render(request, 'index.html', {'movies': movies})

def video_list(request):
    """ Show a list of all videos, limited to 5, sorted by complexity. """
    videos = get_all_videos().order_by('complexity')[:5]
    return render(request, 'video_list.html', {'videos': videos})

def video_detail(request, slug):
    """ Show details for a specific video, including related transcript and options. """
    video = get_video_by_slug(slug)
    return render(request, 'video_detail.html', {'video': video})
