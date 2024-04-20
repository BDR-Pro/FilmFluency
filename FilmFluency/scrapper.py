import os
import django
import sys
import requests
from bs4 import BeautifulSoup
import os
from tqdm import tqdm
import zipfile
import sys
import os
from learning.isitalreadydownloaded import check_if_already_downloaded , movies_without_title , set_title
MOVIETOCLIPS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "MovieToClips")
SRT = os.path.join(MOVIETOCLIPS, "srt")
EXTRACTED_FILES = os.path.join(MOVIETOCLIPS, "extracted_files")
ZIP = os.path.join(MOVIETOCLIPS, "zip")
MOVIES = os.path.join(MOVIETOCLIPS, "movies")

def django_setup():
    sys.path.append('FilmFluency')
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FilmFluency.settings')
    django.setup()

def already_downloaded(movie_title,zip_file):
    
    if zip_file in os.listdir(ZIP) or movie_title in os.listdir(SRT):
        return True 
    if check_if_already_downloaded(movie_title):
        return True
    
    return False

def getlink(pagenumber):
    if pagenumber == 0:
        return "https://www.opensubtitles.org/en/search/sublanguageid-eng/searchonlymovies-on/movielanguage-english/movieimdbratingsign-5/movieimdbrating-4/movieyearsign-5/movieyear-2010/subformat-srt/moviename-++"
    return f"https://www.opensubtitles.org/en/search/sublanguageid-eng/searchonlymovies-on/movielanguage-english/movieimdbratingsign-5/movieimdbrating-4/movieyearsign-5/movieyear-2010/subformat-srt/moviename-++/offset-{pagenumber*40}"

def clean_string(s):
    return s.translate(str.maketrans('', '', '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'))


def remove_extracted_files():
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(parent_dir)
    
    for i in os.listdir(EXTRACTED_FILES):
        file_path = os.path.join(EXTRACTED_FILES, i)
        os.remove(file_path)
    os.removedirs(EXTRACTED_FILES)
    os.makedirs(EXTRACTED_FILES)
def download_english_subtitle(sub_title,sub_id):
        
        
    download_url = f"https://www.opensubtitles.org/en/subtitleserve/sub/{sub_id}"
    # No need to scrape the page for a download link if you know the pattern OpenSubtitles uses
    
    response = requests.get(download_url)
    if response.status_code == 429:
        print("You have been rate limited. Please wait for a while before trying again.")
        sys.exit(1)
    if response.status_code == 200:
        file_path = os.path.join(ZIP, f"{sub_title}.zip")
        with open(file_path, 'wb') as file:
            file.write(response.content)
    else:
        print(f"Failed to fetch the subtitle: Status code {response.status_code}")


def get_list_of_movies(number):
    response = requests.get(getlink(number))
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Hypothetical: finding all links to movie subtitle pages
        movie_links = soup.find_all('a', href=True)
        movie_tiles = [link['href'].split('/')[-1] for link in movie_links if link['href'].startswith('/en/subtitles/')]
        movie_tiles = [clean_string(title) for title in movie_tiles]
        movie_ids = [link['href'].split('/')[-2] for link in movie_links if link['href'].startswith('/en/subtitles/')]
        

        with tqdm(total=len(movie_ids), desc="Downloading subtitles") as pbar:
            for sub_id , movie_tile in zip(movie_ids , movie_tiles):
                zip_file = f"{movie_tile}.zip"
                if already_downloaded(movie_tile,zip_file):
                    pbar.update(1)
                    continue
                download_english_subtitle(movie_tile,sub_id)
                pbar.update(1)
    else:
        print(f"Failed to fetch the list of movies: Status code {response.status_code}")

def extract_srt_files():
    with tqdm(total=len(os.listdir(ZIP)), desc="Extracting SRT files") as pbar:
        for i in os.listdir(ZIP):
            file_path = os.path.join(ZIP, i)
            if file_path.endswith(".zip") and file_path not in os.listdir(SRT):
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(EXTRACTED_FILES)
                os.remove(file_path)
                pbar.update(1)
    
 
def move_srt():
    # Ensure the destination directory exists
    if not os.path.exists("srt"):
        os.makedirs("srt")

    files_to_move = [f for f in os.listdir("extracted_files") if f.endswith(".srt")]
    
    with tqdm(total=len(files_to_move), desc="Moving SRT files") as pbar:
        for item in files_to_move:
            source_path = os.path.join("extracted_files", item)
            destination_path = os.path.join("srt", item)
            
            # Move the .srt file from source to destination
            os.rename(source_path, destination_path)
            
            pbar.update(1)
    remove_extracted_files()
 

def use_it_as_a_module(option=""):
   
    if option == "clean":
        print("Cleaning extracted files")
        remove_extracted_files()
        return
    if option == "extract":
        print("Extracting srt files")
        extract_srt_files()
        move_srt()
        return
    if option == "download":
        download()
        return
    
    with tqdm(total=10, desc="Downloading movies") as pbar:
        print("Downloading movies")
        for i in range(10):
            get_list_of_movies(i)
            pbar.update(1)
    
        print(" \n All movies downloaded")
        extract_srt_files()
        move_srt()
def search_srt(movie_title):
    base_link = f"https://www.opensubtitles.org/ar/search2/sublanguageid-all/moviename-{movie_title}"
    
    response = BeautifulSoup(requests.get(base_link).content, 'html.parser')
    
    if response.find('div', class_='search_results') is None:
        print(f"No results found for {movie_title}")
        return None
    
    movie_link = response.find('div', class_='search_results').find('a')['href']
    movie_id = movie_link.split('/')[-2]
    
    zip_file = f"{movie_title}.zip"
    
    if already_downloaded(movie_title,zip_file):
        return None
    download_english_subtitle(movie_title, movie_id)
    
    print(f"Downloaded {movie_title}")
    
    
    

def search():
    for i in movies_without_title():
        path_srt=search_srt(i.original_title)
        set_title(i,path_srt)
        
        
def create_folders(): 
    if not os.path.exists(MOVIETOCLIPS):
        os.makedirs(MOVIETOCLIPS)
    if not os.path.exists(EXTRACTED_FILES):
        os.makedirs(EXTRACTED_FILES)
    if not os.path.exists(SRT):
        os.makedirs(SRT)
    if not os.path.exists(ZIP):
        os.makedirs(ZIP)
        
import subprocess 
from learning.getAllMovies import getAllMoviesWithoutVideo

def download():
    
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(MOVIES)
    print(os.getcwd())
    print("Downloading movies")
    Movies = getAllMoviesWithoutVideo()
    for i in Movies:
        print(i.original_title)
        #print result stdout
        subprocess.run(["pirate-get",i.original_title,"-0"," --transmission-auth" ,"admin:password"])
      
        