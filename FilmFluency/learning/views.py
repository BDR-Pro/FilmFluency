from django.shortcuts import render
from .models import Video, Movie
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def get_video_with_lowest_complexity():
    try:
        # Ordering by 'complexity' and retrieving the first entry
        video = Video.objects.all().order_by('complexity').first()
        video = video.complexity
    except Video.DoesNotExist:
        video = None
    return video

def get_video_with_highest_complexity():
    try:
        # Ordering by 'complexity' in descending order and retrieving the first entry
        video = Video.objects.all().order_by('-complexity').first()
        video = video.complexity
    except Video.DoesNotExist:
        video = None
    return video


def get_videos_by_complexity(request):
    # Retrieve the complexity level from GET parameters or default to a minimum value
    lowest_complexity = request.GET.get('lowest_complexity', 0)
    videos = Video.objects.filter(complexity__gte=lowest_complexity).order_by('complexity')

    paginator = Paginator(videos, 6)  # Show 6 videos per page
    page = request.GET.get('page')
    try:
        videos = paginator.page(page)
    except PageNotAnInteger:
        videos = paginator.page(1)
    except EmptyPage:
        videos = paginator.page(paginator.num_pages)

    return render(request, 'videos.html', {'videos': videos, 'title':
        lowest_complexity,
        'highest_complexity': get_video_with_highest_complexity(),
        'lowest_complexity': get_video_with_lowest_complexity()
        
        })

def get_videos_by_movie(request, random_slug):
    videos = Video.objects.filter(movie__random_slug=random_slug).order_by('complexity')
    paginator = Paginator(videos, 6)  # Show 5 videos per page
    page = request.GET.get('page')
    try:
        videos = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        videos = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        videos = paginator.page(paginator.num_pages)
    return render(request, 'videos.html', {'videos': videos,'title':videos[0].movie.original_title , 'isitmovie':True})

def get_videos_by_length(request, max_length):
    videos = Video.objects.filter(length__lte=max_length).order_by('complexity')
    paginator = Paginator(videos, 6)  # Show 5 videos per page
    page = request.GET.get('page')
    try:
        videos = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        videos = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        videos = paginator.page(paginator.num_pages)
    return render(request, 'videos.html', {'videos': videos})

def get_unique_movies(request):
    order_by = request.GET.get('orderby', 'rating')  # Default sorting by 'vote_average'
    valid_orderings = ['rating', 'release_date']
    mode = request.GET.get('video_mode', '')
    if order_by not in valid_orderings:
        order_by = 'rating'
    
    country = request.GET.get('country', '')
    if country:
        movies = Movie.objects.filter(country_flag=country).distinct().order_by('-' + order_by)    
    
    if mode == 'true':
        movies = Movie.objects.filter(videos__isnull=False).distinct().order_by('-' + order_by)
            
    else:
        movies = Movie.objects.all().order_by('-' + order_by)     
        
     
    
        
    paginator = Paginator(movies, 6)  # Show 6 movies per page

    page = request.GET.get('page')
    try:
        movies = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        movies = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        movies = paginator.page(paginator.num_pages)
        
    print(f"{mode=}")
    return render(request, 'movies.html', {'movies': movies , 'order_by':order_by , 
                                           'unique_country_flag':list(dict.fromkeys(get_unique_country_flag())), 
                                           'country':country,
                                           'video_mode':mode,
                                           
                                           
                                           })



def get_unique_country_flag():
    return Movie.objects.values_list('country_flag',flat =True ).distinct()




