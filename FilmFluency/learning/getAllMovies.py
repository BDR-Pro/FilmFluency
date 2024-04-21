from .models import Movie
import os

def getAllMoviesWithoutVideo():
    return Movie.objects.filter(videos__isnull=True)



def foo():
    """ Print all movies in the MovieToClips/movies directory. check if the directory is correct. and check if they exist.
    in the db return thier original language
    """
    print(os.getcwd())
    movie = os.path.join(os.getcwd(), "MovieToClips", "movies")
    os.chdir(movie)
    for movie in os.listdir():
        print(movie)
    
    