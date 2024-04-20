import os
import django
import sys

import argparse


# Add the path of your Django project to the system path using realative path
sys.path.insert(0, 'FilmFluency')

# Set the Django settings module environment variable
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FilmFluency.settings')

# Set up Django
django.setup()

from scrapper import use_it_as_a_module
from istextimportant import main as isitimportant
from cleanre import clean_files
from download_movie import main as download
from ffempeg import get_video_and_subtitle
from learning.transcript import populate_and_transcribe
from tmdb_scraper import fill_movie_db, populateDBwithTopMovies
from thumbnail import main as get_thumbnail
from learning.find_word_translate import find_hardest_words , find_not_translated , fill_languages


def create_folders():
    
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(parent_dir)
    MovieToClips = os.path.join(parent_dir, "MovieToClips")
    extracted_files = os.path.join(MovieToClips, "extracted_files")
    srt = os.path.join(MovieToClips, "srt")
    csv_important_text = os.path.join(MovieToClips, "csv_important_text")
    if not os.path.exists("MovieToClips"):
        os.makedirs("MovieToClips")
    if not os.path.exists(extracted_files):
        os.makedirs(extracted_files)
    if not os.path.exists(srt):
        os.makedirs(srt)
    if not os.path.exists(csv_important_text):
        os.makedirs(csv_important_text)

def scrape_srt():
    try:
        use_it_as_a_module()
        use_it_as_a_module("extract")
        use_it_as_a_module("clean")
    except:
        print("Error in scraping srt")
        
def download_from_zip():
    try:
        print("Downloading from zip")
        use_it_as_a_module("download")
    except Exception as e:
        print("Error in downloading from zip\n",e)

def isitimportanttxt():
    try:
        isitimportant()
    except:
        print("Error in isitimportant")
def regex():
    clean_files()


def download_moives():
    try:
        download()
    except:
        print("Error in download")
        
def last_touch():
    get_video_and_subtitle()
    
def main():
    
    parser = argparse.ArgumentParser(description='Process some movies.')
    parser.add_argument('--fill', action='store_true', help='If set, fill the database with top movies')
    parser.add_argument('--download', action='store_true', help='If set, download movies from zip')
    args = parser.parse_args()
    
    if args.download:
        print("Downloading movies")
        download_from_zip()
        print("Movies downloaded")
        sys.exit()
        
    if args.fill:
        populateDBwithTopMovies()
        print("Movies filled")
    
    
    print("Starting the process")
    fill_languages()
    print("Languages filled")
    
    create_folders()
    scrape_srt()
    isitimportanttxt()
    regex()
    download_moives()
    populate_and_transcribe()
    last_touch()
    get_thumbnail()
    find_not_translated()
    find_hardest_words()
    

if __name__ == "__main__":
    main()