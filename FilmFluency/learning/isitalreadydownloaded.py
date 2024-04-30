import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FilmFluency.settings')
django.setup()

from api.upload_to_s3 import upload_to_s3,download_from_s3

from .models import Movie
import requests
from io import BytesIO
from PIL import Image
import subprocess

def check_if_already_downloaded(movie_title):
    if Movie.objects.filter(title__icontains=movie_title).exists():
        return True
    return False

def movies_without_title():
    return Movie.objects.filter(title__isnull=True)

def set_title(movie:Movie,srt_file_path):
    movie.title = srt_file_path
    movie.save()
    
    

def getAllMoviesWithoutVideo():
    return Movie.objects.filter(videos__isnull=True)

def getAllMoviesWithoutSubtitleOrTranscript():
    return Movie.objects.filter(transcript_path__isnull=True, subtitle_path__isnull=True).order_by('rating')


def edit_movie(movie,transcript_path="",subtitle_path=""):
    movie = Movie.objects.get(id=movie.id)
    if transcript_path:
        movie.transcript_path = transcript_path
    if subtitle_path:
        movie.subtitle_path = subtitle_path
    movie.save()
    
    
def fix_erorrs():
    print("Fixing errors")
    Movies = Movie.objects.filter(transcript_path__isnull=False, subtitle_path__isnull=False)
    
    for movie in Movies:
        movie.transcript_path = None
        movie.subtitle_path = None
        movie.save()

def download_image(url):
    """Download image from url to harddrive and return the image path"""
    print(f"Downloading image from \n {url}")
    response = requests.get(url)
    image = Image.open(BytesIO(response.content))
    image_path = "temp.jpg"
    image.save(image_path)
    return image_path  

def delete_image(img):
    os.remove(img)
    
def convert_to_webp(img):
    """Convert image to webp format using magick"""
    subprocess.run(["magick", img, img.replace("jpg","webp")]) 
    os.remove(img)


def upload_image_to_s3():
    allmovies=Movie.objects.all().count()
    index=0
    for movie in Movie.objects.all().order_by('trendingmovies__views'):
        index+=1
        if movie.poster == None:
            continue
        if not 'tmdb' in movie.poster:
            continue
        print(f"Uploading image for {movie.title}")
        print(f"Processing {index} of {allmovies}")
        image_path = download_image(movie.poster)
        convert_to_webp(image_path)
        uploaded=upload_to_s3(image_path.replace("jpg","webp"),"posters/"+movie.title + ".webp")
        if uploaded:
            movie.poster = "/posters/"+movie.title + ".webp"
            movie.save()