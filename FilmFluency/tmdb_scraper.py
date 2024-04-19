import requests
import os
import re
from learning.models import Movie  
from imdb import IMDb
import random
from urllib.parse import quote
from datetime import datetime
from pathlib import Path
from api.upload_to_s3 import upload_to_s3
from django.conf import settings

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
    os.chdir(image_dir)
    path_=os.path.join(title,image_path)
    if url:
        response = requests.get(url)
        if response.status_code == 200:
            image_path = f'poster{random_string()}.jpg'
            with open(image_path, 'wb') as file:
                file.write(response.content)
                
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
        link = f"https://image.tmdb.org/t/p/original{poster_path}"
        return quote(link)
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
    if movie := Movie.objects.filter(title=title).first():
        print(f"Movie already exists: {movie.title}")
        return
    if movie := Movie.objects.filter(original_title=title).first():
        fill_already_existing_movie(movie,title)
        return
    
    normalized_title = normalize_title(title)
    imdb_id = search_imdb_id(normalized_title)
    movie_data = fetch_movie_data_by_id(imdb_id)
    movie_data = movie_data['movie_results'][0] if movie_data else None
    if movie_data:
        try:
            movie = Movie.objects.create(
                tmdb_id=movie_data['id'],
                title=title,  # Assuming 'title' is a variable you've already defined
                original_title=movie_data.get('original_title', ''),
                description=movie_data.get('overview', ''),
                type=movie_data.get('media_type', 'movie'),  # Ensure 'type' field exists in your model
                release_date=movie_data.get('release_date'),
                rating=movie_data.get('vote_average', 0),
                backdrop_path=get_poster_url('backdrop_path'),
                poster=image_path(title,get_poster_url(movie_data.get('backdrop_path'))),
                original_language=movie_data.get('original_language', ''),
                popularity=movie_data.get('popularity', 0),
                vote_average=movie_data.get('vote_average', 0),
                vote_count=movie_data.get('vote_count', 0)
            )
            print(f"New movie created: {movie.title}")
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



def is_time_to_update(last_call_time):
    """Check if it's been a week since the last API call."""
    if (datetime.datetime.now() - last_call_time).days >= 7:
        return True
    return False

def update_movies():
    print("Updating movies...")
    print("Fetching top movies...")
    print("Number of Movies",Movie.objects.all().count())
    last_call_path = Path('calls.txt')
    if last_call_path.exists():
        last_call_time = datetime.datetime.fromisoformat(last_call_path.read_text().strip())
        if not is_time_to_update(last_call_time):
            return "No need to update yet."

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
    last_call_path.write_text(datetime.datetime.now().isoformat())

def populateDBwithTopMovies():
    print("Populating database with top movies...")
    try:
        if not is_it_one_week_yet():
            return
        update_movies()
    except Exception as e:
        print(f"Error updating movies: {str(e)}")

def is_it_one_week_yet():
    """Check if a week has passed since the last successful call."""
    try:
        with open('calls.txt', 'r') as file:
            last_call = datetime.datetime.fromisoformat(file.read().strip())
            return is_time_to_update(last_call)
    except FileNotFoundError:
        # If file not found, assume it's time for an update
        return True

def fill_with_random_movies():
    """Fill the database with random movies."""
    for i in range(10):
        fetch_movies('popular')