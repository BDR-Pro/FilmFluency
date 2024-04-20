from .models import Movie


def getAllMoviesWithoutVideo():
    return Movie.objects.filter(videos__isnull=True)