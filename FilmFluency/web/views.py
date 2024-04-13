# views.py
from django.shortcuts import render, get_object_or_404
from django.db.models import F
from learning.models import Video, TrendingMovies

def getAllVideos():
    """ Return all videos in the database. """
    return Video.objects.all()

def getVideoById(video_id):
    """ Return a specific video by its ID. """
    # Ensure the video exists or return a 404 error
    video = get_object_or_404(Video, pk=video_id)
    # Safely increment views using F() to avoid race conditions
    TrendingMovies.objects.filter(title=video.movie).update(views=F('views') + 1)
    return video

def getTrendingMovies():
    """ Return top 5 trending movies based on views. """
    return TrendingMovies.objects.order_by('-views')[:5]

def home(request):
    """ Render the homepage with introductory information. """
    movies = getTrendingMovies()
    return render(request, 'index.html', {'movies': movies})

def video_list(request):
    """ Show a list of all videos sorted by complexity. """
    videos = getAllVideos().order_by('Complexity')
    return render(request, 'video_list.html', {'videos': videos})

def video_detail(request, video_id):
    """ Show details for a specific video, including related transcript and options. """
    video = getVideoById(video_id)
    return render(request, 'video_detail.html', {'video': video})
