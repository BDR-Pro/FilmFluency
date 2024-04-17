import os
import django
import sys



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
from turn_it_into_mp3 import main as turn_it_into_mp3
from MovieToClips.find_word_translate import find_hardest_words , find_not_translated , fill_languages


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
    use_it_as_a_module()
    use_it_as_a_module("extract")
    use_it_as_a_module("clean")
    

def isitimportanttxt():
    isitimportant()
    
def regex():
    clean_files()


def download_moives():
    download()
    
def last_touch():
    get_video_and_subtitle()
    
    
def main():
    fill_languages()
    populateDBwithTopMovies()
    populate_and_transcribe()
    create_folders()
    scrape_srt()
    isitimportanttxt()
    regex()
    download_moives()
    last_touch()
    fill_movie_db()
    get_thumbnail()
    turn_it_into_mp3()
    find_not_translated()
    find_hardest_words()
    
    
if __name__ == "__main__":
    main()