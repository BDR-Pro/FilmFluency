import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FilmFluency.settings')
django.setup()

from .models import Movie

def check_if_already_downloaded(movie_title):
    if Movie.objects.filter(title__icontains=movie_title).exists():
        return True
    return False

def movies_without_title():
    return Movie.objects.filter(title__isnull=True)

def set_title(movie:Movie,srt_file_path):
    movie.title = srt_file_path
    movie.save()
    
    

def getAllMoviesWithoutVideo():
    return Movie.objects.filter(videos__isnull=True)

def getAllMoviesWithoutSubtitleOrTranscript():
    return Movie.objects.filter(transcript_path__isnull=True, subtitle_path__isnull=True).order_by('rating')


def edit_movie(movie,transcript_path="",subtitle_path=""):
    movie = Movie.objects.get(id=movie.id)
    if transcript_path:
        movie.transcript_path = transcript_path
    if subtitle_path:
        movie.subtitle_path = subtitle_path
    movie.save()
    
    
def fix_erorrs():
    print("Fixing errors")
    Movies = Movie.objects.filter(transcript_path__isnull=False, subtitle_path__isnull=False)
    
    for movie in Movies:
        movie.transcript_path = None
        movie.subtitle_path = None
        movie.save()