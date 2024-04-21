from django.shortcuts import render, get_object_or_404
from django.db.models import F
from learning.models import Video, TrendingMovies, Movie
from users.models import UserProgress
from django.db.models import Max
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from learning.views import get_unique_country_flag


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
    

def get_all_videos():
    """ Return all videos in the database. """
    return Video.objects.all()

def get_video_by_slug(slug):
    """ Return a specific video by its unique slug. """
    video = get_object_or_404(Video, random_slug=slug)
    
    # Ensure that a TrendingMovies object exists for this movie, or create a new one
    trending_movie, created = TrendingMovies.objects.get_or_create(movie=video.movie, defaults={'views': 0})
    
    # Increment views only if the object wasn't just created
    if not created:
        TrendingMovies.objects.filter(pk=trending_movie.pk).update(views=F('views') + 1)
    
    return video

@login_required(login_url='users:login')
def video_detail(request, random_slug):
    """ Show details for a specific video, including related transcript and options. """
    user_progress = UserProgress.objects.get(user=request.user)
    if user_progress.paid_user:
        if request.method == 'POST':
            video = get_video_by_slug(random_slug)
            user_progress = UserProgress.objects.get(user=request.user)
            user_progress.videos_watched.add(video)
            user_progress.points += video.complexity
            user_progress.highest_score = max(user_progress.highest_score, video.complexity)
            user_progress.watched_movies.add(video.movie)
            user_progress.check_and_update_level()
            user_progress.known_languages.add(video.movie.original_language)
            user_progress.save()
            return redirect('web:home')
        video  = get_video_by_slug(random_slug)
        return render(request, 'video_detail.html', {'video': video })
    else:
        return redirect('payment:payment')

def get_movie_by_slug(request,random_slug):
    """ Return a specific movie by its unique slug. """
    movie = get_object_or_404(Movie, random_slug=random_slug)  
    isittrendy = TrendingMovies.objects.get_or_create(movie=movie)
    views=isittrendy[0].views
    does_it_have_videos = Video.objects.filter(movie=movie).count() > 0
    return render(request, 'movie_detail.html', {'movie': movie, 'views': views, 'does_it_have_videos': does_it_have_videos})

def get_trending_movies():
    return Movie.objects.filter(trendingmovies__isnull=False).order_by('-trendingmovies__views')

def get_latest_updated_movies():
    return Movie.objects.order_by('-date_added')

def get_latest_movies():
    return Movie.objects.order_by('-release_date')

def home(request):
    """ Render the homepage with introductory information and top trending movies based on user selection or cookie. """
    
    # Default source
    default_source = 'trending'
    if 'reset_preferences' in request.GET:
        response = redirect('web:home')  # Assuming 'home' is the name of the URL pattern for this view
        response.delete_cookie('preferred_movies')
        response.delete_cookie('country')
        return response
    # Check if there is a user preference in cookies or use the default
    user_choice = request.COOKIES.get('preferred_movies', default_source)
    country_flag = request.COOKIES.get('country', '')
    
    # Check if a new choice has been made via GET request
    if 'source' in request.GET:
        user_choice = request.GET['source']
    
    if 'country' in request.GET:
        country_flag = request.GET['country']
        
    # Map source names to function calls
    movie_sources = {
        'trending': get_trending_movies,
        'latest_updated': get_latest_updated_movies,
        'latest': get_latest_movies
    }
    
    # Fetch movies from the chosen source
    movies = movie_sources.get(user_choice, get_trending_movies)()
    if country_flag:
        movies = movies.filter(country_flag=country_flag)  # Assuming Movie model has 'country_flag' attribute
    
    message = f"{user_choice.replace('_', ' ').title()} Movies"
    
    # Render response with initial movie data
    response = render(request, 'index.html', {
        'movies': movies[:5],  # Limit to 5 movies for simplicity
        'message': message,
        'current_source': user_choice,
        'unique_country_flag': get_unique_country_flag(),
        'current_country': country_flag
    })
    if not 'reset_preferences' in request.GET:

        # Set/update cookie for user's movie source preference and country
        response.set_cookie('preferred_movies', user_choice, max_age=30*24*60*60)  # Expires in 30 days
        response.set_cookie('country', country_flag, max_age=30*24*60*60)  # Expires in 30 days
        
    return response



def video_list(request):
    # Get the orderby parameter from the URL or default to 'complexity'
    order_by = request.GET.get('orderby', 'complexity')
    valid_sorts = ['length', 'date_added', 'complexity']

    # Determine the ordering parameter
    if order_by.lstrip('-') in valid_sorts:
        # Append '-' for descending unless it's 'date_added' which we might want ascending
        order_by_param = f"-{order_by}" if order_by != 'date_added' else order_by
    else:
        # Reset to default order if provided value is not valid
        order_by = 'complexity'
        order_by_param = '-complexity'
    
    # Retrieve videos ordered by the specified field
    all_videos = Video.objects.all().order_by(order_by_param)
    
    # Setup paginator
    paginator = Paginator(all_videos, 5)  # Show 5 videos per page
    page = request.GET.get('page')
    
    try:
        videos = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        videos = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page of results.
        videos = paginator.page(paginator.num_pages)

    # Remove hyphen from current_order for display purposes in the template
    current_order = order_by.lstrip('-')
    return render(request, 'video_list.html', {'videos': videos, 'current_order': current_order})


def random_movie(request):
   
    random_movie = Movie.objects.order_by('?').first()
    
    redirect_url = f'/movie/{random_movie.random_slug}/'
    
    return redirect(redirect_url)


def search_movies(request):
    query = request.GET.get('query')
    movies = Movie.objects.filter(title__icontains=query)
    if not movies:
        return render(request, 'movies.html', {'no_res': True})
    return render(request, 'movies.html', {'movies': movies, 'query': query})