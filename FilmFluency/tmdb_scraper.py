import requests
import os
import csv
import re
from learning.models import Movie  
import random
from api.upload_to_s3 import upload_to_s3
from django.conf import settings
import random
from django.db.models import Count
from django.utils import timezone
import logging

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE_URL = "https://api.themoviedb.org/3"



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

def get_country_flag(original_language):
    # Mapping from language codes to country flags using ISO 3166-1 alpha-2 codes
    language_to_country = {
        'en': 'US',  # English
        'es': 'ES',  # Spanish
        'fr': 'FR',  # French
        'de': 'DE',  # German
        'it': 'IT',  # Italian
        'pt': 'PT',  # Portuguese
        'ru': 'RU',  # Russian
        'ja': 'JP',  # Japanese
        'zh': 'CN',  # Chinese
        'ko': 'KR',  # Korean
        'sv': 'SE',  # Swedish
        'da': 'DK',  # Danish
        'pl': 'PL',  # Polish
        'nl': 'NL',  # Dutch
        'hi': 'IN',  # Hindi
        'ar': 'SA',  # Arabic
        'he': 'IL',  # Hebrew
        'th': 'TH',  # Thai
        'cs': 'CZ',  # Czech
        'tr': 'TR',  # Turkish
        'fi': 'FI',  # Finnish
        'hu': 'HU',  # Hungarian
        'no': 'NO',  # Norwegian
        'el': 'GR'   # Greek
    }
    return language_to_country.get(original_language, 'ZZ')


def get_poster_url(poster_path):
    """Construct full URL for movie poster."""
    if poster_path:
        return f"https://image.tmdb.org/t/p/original{poster_path}"
    return None


def normalize_title(title):
    """Normalize movie titles to remove year and resolution details."""
    if "(" in title:
        title = title.split("(")[0].strip()
    return title

def read_and_process_csv(file_path):
    """Read CSV file and process each row."""
    movies = []
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                # Create a movie instance for each row
                movie = Movie(
                    title=normalize_title(row.get('title', '')),
                    genre=row.get('genres', 'Unknown'),
                    description=row.get('overview', ''),
                    release_date=row.get('release_date'),
                    rating=float(row.get('vote_average', 0)),
                    poster=get_poster_url(row.get('poster_path')),
                    tmdb_id=int(row.get('id', 0)),
                    original_title=row.get('original_title', ''),
                    original_language=row.get('original_language', 'en'),
                    country_flag=get_country_flag(row.get('original_language')),
                    popularity=float(row.get('popularity', 0)),
                    vote_count=int(row.get('vote_count', 0)),
                    budget=int(row.get('budget', 0)),
                    revenue=int(row.get('revenue', 0)),
                    runtime=int(row.get('runtime', 0)),
                    homepage=row.get('homepage'),
                    date_added=timezone.now(),
                    status=row.get('status', 'Unknown'),
                    tagline=row.get('tagline', ''),
                    production_companies=row.get('production_companies', ''),
                    production_countries=row.get('production_countries', ''),
                    spoken_languages=row.get('spoken_languages', ''),
                    keywords=row.get('keywords', '')
                )
                movies.append(movie)
            except Exception as e:
                # Log an error message
                logging.error(f"Error processing row: {e}")
    return movies

    


def bulk_insert_movies(movies):
    """Insert list of Movie instances into the database."""
    Movie.objects.bulk_create(movies, ignore_conflicts=True)

def read_and_process_csv_credits(file_path):
    """Read CSV file and process each row."""
    movies = []
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Create a movie instance for each row movie_id,title,cast,crew
            movie = Movie.objects.get(tmdb_id=int(row['movie_id']))
            movie.cast = row['cast']
            movie.crew = row['crew']
            movies.append(movie)
    return movies

def import_movies_from_csv():
    """Main function to import movies from a CSV file."""
    print("Starting the import process...")
    file_path = 'tmdb_csv'
    file_path = os.path.join(file_path, 'tmdb_5000_movies.csv')
    movies = read_and_process_csv(file_path)
    print(f"Importing {len(movies)} movies into the database...")
    bulk_insert_movies(movies)
    print("Import process completed successfully.")
    #do it for the credits file
    file_path = 'tmdb_csv'
    file_path = os.path.join(file_path, 'tmdb_5000_credits.csv')
    movies = read_and_process_csv_credits(file_path)
    print(f"Importing {len(movies)} movies into the database...")
    

# Call the function to start the import process

        
    
  
def update_movies():
    print("Updating movies...")
    print("Fetching top movies...")
    print("delete dubplicate movies...")
    print("Number of Movies", Movie.objects.all().count())
    #counter to count the number of movies fetched
    import_movies_from_csv()

        
    # Record the time of this call

def populateDBwithTopMovies():
    print("Populating database with top movies...")
    update_movies()


