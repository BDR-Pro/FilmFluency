import requests
import os
import re
from learning.models import Movie  
from imdb import IMDb
import random
from datetime import datetime
from pathlib import Path
from api.upload_to_s3 import upload_to_s3
from django.conf import settings


def create_dir(path):
    """Create a directory if it doesn't exist."""
    if not os.path.exists(path):
        os.makedirs(path)
    
def random_string():
    """Generate a random string of 6 characters."""
    return ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=6))

TMDB_API_KEY = settings.TMDB_API_KEY
TMDB_BASE_URL = 'https://api.themoviedb.org/3'

def image_path(title,url):
    """Download image from URL and return path to local file."""
    image_dir=os.path.join(os.path.dirname(os.path.abspath(__file__)),f'MovieToClips')
    image_dir=os.path.join(image_dir,'cut_videos')
    image_dir=os.path.join(image_dir,f'{title}')
    create_dir(image_dir)
    os.chdir(image_dir)
    if url:
        response = requests.get(url)
        if response.status_code == 200:
            image_path = f'poster{random_string()}.jpg'
            with open(image_path, 'wb') as file:
                file.write(response.content)
            path_=os.path.join(title,image_path)
            return upload_to_s3(path_,'.jpg')
    
    return None
    
def search_imdb_id(title):
    """Search for a movie by title and return its IMDB ID with 'tt' prefix using imdbpy."""
    ia = IMDb()
    results = ia.search_movie(title)
    if results:
        # Append 'tt' to the numeric ID to form a standard IMDb ID.
        imdb_id = 'tt' + results[0].movieID
        print(imdb_id)
        return imdb_id
    return None


def get_poster_url(poster_path):
    """Construct full URL for movie poster."""
    if poster_path:
        return f"https://image.tmdb.org/t/p/original{poster_path}"
    return None

def fetch_movie_data_by_id(tmdb_id):
    """Fetch detailed movie data from TMDB by TMDB ID."""
    url = f"{TMDB_BASE_URL}/find/{tmdb_id}?external_source=imdb_id"
    params = {
        'api_key': TMDB_API_KEY
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    return None

def normalize_title(title):
    """Normalize movie titles extracted from encoded strings."""
    # Remove resolution and everything after it
    title = re.sub(r'\d{3,4}p.*$', '', title) 
    # Attempt to extract a title and a year
    match = re.search(r"([\w\s]+)(\d{4})", title)
    if match:
        movie_title = match.group(1).strip()  # Trim whitespace
        year = match.group(2)
        return f"{movie_title} ({year})"
    return title  # Return the original if no match found

def fill_already_existing_movie(movie:Movie,title):
    movie.title = title
    movie.save()
    print(f"Movie title updated: {movie.title}")
    
def fill_movie_db(title):
    """Process a title and update or create a movie record in the database."""
   
    normalized_title = normalize_title(title)
    imdb_id = search_imdb_id(normalized_title)
    movie_data = fetch_movie_data_by_id(imdb_id)
    try:
        movie_data = movie_data['movie_results'][0] if movie_data else None
    except:
        movie_data = None
        
    if movie_data:
        try:
        # Corrected to use actual data from movie_data
            backdrop_url = get_poster_url(movie_data.get('backdrop_path'))
            poster_url = get_poster_url(movie_data.get('poster_path'))  # Assuming there is a 'poster_path'

            movie = Movie.objects.create(
                tmdb_id=movie_data['id'],
                title=title,
                original_title=movie_data.get('original_title', ''),
                description=movie_data.get('overview', ''),
                type=movie_data.get('media_type', 'movie'),
                release_date=movie_data.get('release_date'),
                rating=movie_data.get('vote_average', 0),
                backdrop_path=backdrop_url,
                poster=poster_url,
                original_language=movie_data.get('original_language', ''),
                popularity=movie_data.get('popularity', 0),
                vote_average=movie_data.get('vote_average', 0),
                vote_count=movie_data.get('vote_count', 0)
            )
        except Exception as e:
            print(f"Error creating movie: {str(e)}")
    else:
        print("No data found for:", normalized_title)
        
        


def fetch_movies(category, genre_id=None, language=None):
    """Fetch movies based on category, optional genre, and language."""
    url = f"{TMDB_BASE_URL}/movie/{category}"
    params = {
        'api_key': TMDB_API_KEY,
        'page': 1
    }
    if genre_id:
        params['with_genres'] = genre_id
    if language:
        params['language'] = language

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        for movie in data['results']:
            fill_movie_db(movie['title'])



def update_movies():
    print("Updating movies...")
    print("Fetching top movies...")
    print("Number of Movies",Movie.objects.all().count())
 
    movie_types = {
        'top_rated': None,
        'latest': None,
        'popular': None,
        'now_playing': None,
        'genres': {
            '10751': 'Top Family',
            '28': 'Top Action',
            '35': 'Top Comedy',
            '27': 'Top Horror',
            '10749': 'Top Romance',
            '99': 'Top Documentary',
            '878': 'Top Sci-Fi',
            '16': 'Top Animation',
            '10402': 'Top Musical',
            '12': 'Top Adventure',
            '9648': 'Top Mystery',
            '18': 'Top Drama',
            '14': 'Top Fantasy',
            '36': 'Top History',
            '10752': 'Top War',
            '37': 'Top Western',
            '53': 'Top Thriller',
        },

        'languages': {
            'fr': 'French',
            'de': 'German',
            'es': 'Spanish'
        }
    }


    # Fetch by genre
    for key, genre_id in movie_types.get('genres', {}).items():
        fetch_movies('top_rated', key)

    # Fetch by language
    for lang_code, lang_description in movie_types.get('languages', {}).items():
        fetch_movies('popular', None, lang_code)
        
    # Record the time of this call

def populateDBwithTopMovies():
    print("Populating database with top movies...")
    update_movies()


def fill_with_random_movies():
    """Fill the database with random movies."""
    for i in range(1000):
        fetch_movies('popular')