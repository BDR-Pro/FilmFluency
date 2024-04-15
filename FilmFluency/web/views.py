from django.shortcuts import render, get_object_or_404
from django.db.models import F
from learning.models import Video, TrendingMovies, Movie
from django.db.models import Max


def get_latest_updated_movies():
    """ Return the 5 most recently added movies based on their associated videos. """
    try:
    # First, annotate each movie with the latest date a related video was added
        recent_movies = Movie.objects.annotate(
            latest_video_date=Max('videos__date_added')
        ).order_by('-latest_video_date')[:5]  # Order by this annotated field in descending order

        return recent_movies
    except:
        return None
    
def get_latest_movies():
    try:
        """ Return the 5 most recently added movies. """
    # Ensure the Movie model has a 'date_added' field
        return Movie.objects.order_by('-date_added')[:5]
    except:
        return None
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
    movies = get_latest_updated_movies() if not movies else movies
    movies = get_latest_movies() if not movies else movies
    return render(request, 'index.html', {'movies': movies})

def video_list(request):
    """ Show a list of all videos, limited to 5, sorted by complexity. """
    videos = get_all_videos().order_by('complexity')[:5]
    return render(request, 'video_list.html', {'videos': videos})

def video_detail(request, slug):
    """ Show details for a specific video, including related transcript and options. """
    video = get_video_by_slug(slug)
    return render(request, 'video_detail.html', {'video': video})
