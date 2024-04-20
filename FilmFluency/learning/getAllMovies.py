from .models import Movie


def getAllMoviesWithoutVideo():
    return Movie.objects.filter(video__isnull=True)