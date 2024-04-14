import requests
from FilmFluency.learning.models import Movie, Video
from dotenv import load_dotenv
import os
load_dotenv()
TMDB_API_KEY = os.getenv('TMDB_API_KEY')
TMDB_BASE_URL = 'https://api.themoviedb.org/3'

def fetch_movie_data(title):
    """Fetch movie data from TMDB by title."""
    url = f"{TMDB_BASE_URL}/search/movie"
    params = {
        'api_key': TMDB_API_KEY,
        'query': title
    }
    response = requests.get(url, params=params)
    results = response.json().get('results')
    if results:
        return results[0]  # Return the first result
    return None

def fill_movie_db():
    """Fill the movie database by fetching data from TMDB."""
    movies = Video.objects.all().distinct('movie')
    for video in movies:
        title = video.movie
        if Movie.poster_url is None:
            movie_data = fetch_movie_data(title)
            if movie_data:
                Movie.objects.create(
                    title=title,
                    description=movie_data.get('overview', ''),
                    release_date=movie_data.get('release_date', None),
                    rating=movie_data.get('vote_average', 0),
                    poster=get_poster_url(movie_data.get('poster_path')),
                )
                print(f"Added {title} to the database.")

def get_poster_url(poster_path):
    if poster_path:
        return f"https://image.tmdb.org/t/p/original{poster_path}"
    return None

