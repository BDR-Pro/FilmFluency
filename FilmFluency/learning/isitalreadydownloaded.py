from .models import Movie
def check_if_already_downloaded(movie_title):
    if Movie.objects.filter(title__icontains=movie_title).exists():
        return True
    return False