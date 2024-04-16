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