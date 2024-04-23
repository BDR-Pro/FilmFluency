import os
import csv
import requests
import json
import logging
from datetime import datetime
from django.utils import timezone
from learning.models import Movie, Country, Language
from django.db.models import ObjectDoesNotExist
import pycountry

logging.basicConfig(level=logging.INFO)

# Environment Variables
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE_URL = "https://api.themoviedb.org/3/movie/"




def get_genre(tmdb_id):
    """ Retrieve the genre of a movie from the TMDB API. """
    response = requests.get(f"{TMDB_BASE_URL}{tmdb_id}", params={'api_key': TMDB_API_KEY})
    if response.status_code == 200:
        data = response.json()
        genre = data.get('genres')[0].get('name')
        return genre
    return None

def find_language_name(iso_639_1):
    """ Retrieve the English name of a language from its ISO 639-1 code using TMDB API. """
    response = requests.get(f"https://api.themoviedb.org/3/configuration/languages?api_key={TMDB_API_KEY}")
    if response.status_code == 200:
        languages = response.json()
        for language in languages:
            if language['iso_639_1'] == iso_639_1:
                return language['english_name']
    return None



def normalize_title(title):
    """ Normalize movie titles by removing unnecessary parts. """
    return title.split('[')[0].strip()

def get_poster_url(tmdb_id):
    """ Retrieve the full URL for a movie poster. """
    response = requests.get(f"{TMDB_BASE_URL}{tmdb_id}", params={'api_key': TMDB_API_KEY})
    if response.status_code == 200:
        data = response.json()
        poster_path = data.get('poster_path')
        return f"https://image.tmdb.org/t/p/original{poster_path}" if poster_path else None
    return None

def read_and_process_csv(file_path, using='default'):
    """ Read and process movie data from CSV file. """
    movies = []
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        total_rows = sum(1 for row in csv.reader(open(file_path)))
        current_row = 0
        csvfile.seek(0)  # Reset CSV file position after counting
        next(reader)  # Skip header
        for row in reader:
            
            current_row += 1
            percentage_complete = (current_row / total_rows) * 100
            logging.info(f"Processing row {current_row}/{total_rows} ({percentage_complete:.2f}%)")
            logging.info(f"Processing Movie: {row['title']}")
            try:
                Movie.objects.create(
                    title=normalize_title(row['title']),
                    description=row['overview'],
                    release_date=datetime.strptime(row['release_date'], '%Y-%m-%d').date() if row['release_date'] else None,
                    rating=float(row['vote_average']),
                    poster=get_poster_url(row['id']),
                    tmdb_id=int(row['id']),
                    genre=get_genre(row['id']),
                    original_title=row['original_title'],
                    original_language=row['original_language'],
                    popularity=float(row['popularity']),
                    vote_count=int(row['vote_count']),
                    budget=int(row['budget']),
                    revenue=int(row['revenue']),
                    runtime=int(row['runtime']),
                    homepage=row['homepage'],
                    date_added=timezone.now(),
                )
                
                
            except Exception as e:
                logging.error(f"Error processing row: {e}")
    return movies



def populateDBwithTopMovies():
    """ Populate the database with movie data from a CSV file. """
    print(f"{len(Movie.objects.all())=}")
    file_path = os.path.join('tmdb_csv', 'tmdb_5000_movies.csv')
    movies = read_and_process_csv(file_path)
