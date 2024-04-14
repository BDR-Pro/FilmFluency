from scrapper import use_it_as_a_module
from istextimportant import main as isitimportant
from cleanre import clean_files
import os
from download_movie import main as download
from ffempeg import get_video_and_subtitle
from FilmFluency.learning.transcript import populate_and_transcribe
from tmdb_scraper import fill_movie_db

def create_folders():
    if not os.path.exists("extracted_files"):
        os.makedirs("extracted_files")
    if not os.path.exists("srt"):
        os.makedirs("srt")
    if not os.path.exists("csv_important_text"):
        os.makedirs("csv_important_text")

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
    get_video_and_subtitle
    
    
def main():
    populate_and_transcribe()
    create_folders()
    scrape_srt()
    isitimportanttxt()
    regex()
    download_moives()
    last_touch()
    fill_movie_db()
    

if __name__ == "__main__":
        main()
        