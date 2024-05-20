import requests
from django.conf import settings
from datetime import datetime
from api.upload_to_s3 import upload_to_s3
from django.conf import settings

def is_it_a_valid_imdb_id(slug_or_id):
    if len(slug_or_id) == 9 and slug_or_id.startswith('tt'):
        imdb_id = slug_or_id
        url = f"https://api.themoviedb.org/3/find/{imdb_id}?api_key={settings.TMDB_API_KEY}&external_source=imdb_id"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data.get('movie_results'):
                return True
                
    return False


def get_movie_data_from_tmdb(imdb_id):
    api_key = settings.TMDB_API_KEY
    base_url = 'https://api.themoviedb.org/3'

    # Search for the movie by IMDb ID
    search_url = f'{base_url}/find/{imdb_id}'
    search_params = {
        'api_key': api_key,
        'external_source': 'imdb_id'
    }
    
    response = requests.get(search_url, params=search_params)
    
    if response.status_code == 200:
        search_results = response.json()
        if search_results['movie_results']:
            movie_id = search_results['movie_results'][0]['id']
            
            # Get the movie details by TMDb movie ID
            movie_url = f'{base_url}/movie/{movie_id}'
            movie_params = {
                'api_key': api_key,
            }
            
            movie_response = requests.get(movie_url, params=movie_params)
            
            if movie_response.status_code == 200:
                movie_data = movie_response.json()
                
                # Map the TMDb data to your Django model fields
                movie_data_mapped = {
                    'title': movie_data.get('title', ''),
                    'description': movie_data.get('overview', ''),
                    'genre': ', '.join([genre['name'] for genre in movie_data.get('genres', [])]),
                    'release_date': datetime.strptime(movie_data['release_date'], '%Y-%m-%d') if movie_data.get('release_date') else None,
                    'rating': movie_data.get('vote_average', 0),
                    'poster': upload_poster_to_s3(f"https://image.tmdb.org/t/p/original{movie_data.get('poster_path', '')}", movie_data.get('title', '')),
                    'tmdb_id': movie_data.get('id'),
                    'original_title': movie_data.get('original_title', ''),
                    'original_language': movie_data.get('original_language', ''),
                    'popularity': movie_data.get('popularity', 0),
                    'vote_count': movie_data.get('vote_count', 0),
                    'budget': movie_data.get('budget', 0),
                    'revenue': movie_data.get('revenue', 0),
                    'runtime': movie_data.get('runtime', 0),
                    'homepage': movie_data.get('homepage', ''),
                }
                return movie_data_mapped
            else:
                return {'error': f'Failed to retrieve movie details: {movie_response.status_code}'}
        else:
            return {'error': 'Movie not found on TMDb'}
    else:
        return {'error': f'Failed to search for movie: {response.status_code}'}


def upload_poster_to_s3(poster_url, title):
    try:
        response = requests.get(poster_url)
        if response.status_code == 200:
            file_name = f"{title}.jpg"
            with open(file_name, 'wb') as f:
                f.write(response.content)
            upload_to_s3(file_name, key=f"posters/{file_name}")
            return f"posters/{file_name}"
    except Exception as e:
        print(f"Error uploading poster: {str(e)}")
    return False