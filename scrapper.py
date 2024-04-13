import requests
from bs4 import BeautifulSoup
import os
from tqdm import tqdm
import zipfile
import sys
from FilmFluency.learning.models import Video
     
if not os.path.exists("srt"):
    os.makedirs("srt")
if not os.path.exists("zip"):
    os.makedirs("zip")
if not os.path.exists("extracted_files"):
    os.makedirs("extracted_files")

def already_downloaded(movie_title,zip_file):
    
    if zip_file in os.listdir("zip") or movie_title in os.listdir("srt"):
        return True 
    if Video.objects.filter(movie=movie_title).exists():
        return True
    if Video.objects.filter(movie_icontains=movie_title).exists():
        return True
    
    return False

def getlink(pagenumber):
    if pagenumber == 0:
        return "https://www.opensubtitles.org/en/search/sublanguageid-eng/searchonlymovies-on/movielanguage-english/movieimdbratingsign-5/movieimdbrating-4/movieyearsign-5/movieyear-2010/subformat-srt/moviename-++"
    return f"https://www.opensubtitles.org/en/search/sublanguageid-eng/searchonlymovies-on/movielanguage-english/movieimdbratingsign-5/movieimdbrating-4/movieyearsign-5/movieyear-2010/subformat-srt/moviename-++/offset-{pagenumber*40}"

def clean_string(s):
    return s.translate(str.maketrans('', '', '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'))


def remove_extracted_files():
    for i in os.listdir("extracted_files"):
        file_path = os.path.join("extracted_files", i)
        os.remove(file_path)
    os.removedirs("extracted_files")
    os.makedirs("extracted_files")
def download_english_subtitle(sub_title,sub_id):
        
        
    download_url = f"https://www.opensubtitles.org/en/subtitleserve/sub/{sub_id}"
    # No need to scrape the page for a download link if you know the pattern OpenSubtitles uses
    
    response = requests.get(download_url)
    if response.status_code == 429:
        print("You have been rate limited. Please wait for a while before trying again.")
        sys.exit(1)
    if response.status_code == 200:
        file_path = os.path.join("zip", f"{sub_title}.zip")
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
    with tqdm(total=len(os.listdir("zip")), desc="Extracting SRT files") as pbar:
        for i in os.listdir("zip"):
            file_path = os.path.join("zip", i)
            if file_path.endswith(".zip") and file_path not in os.listdir("srt"):
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall("extracted_files")
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
        remove_extracted_files()
        return
    if option == "extract":
        extract_srt_files()
        move_srt()
        return
    with tqdm(total=10, desc="Downloading movies") as pbar:
        for i in range(10):
            get_list_of_movies(i)
            pbar.update(1)
    
        print(" \n All movies downloaded")
        extract_srt_files()
        move_srt()
       

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "clean":
            remove_extracted_files()
            return
        if sys.argv[1] == "extract":
            extract_srt_files()
            move_srt()
            return
    with tqdm(total=10, desc="Downloading movies") as pbar:
        for i in range(10):
            get_list_of_movies(i)
            pbar.update(1)
    
        print(" \n All movies downloaded")
        extract_srt_files()
        move_srt()

if __name__ == "__main__":
    main()


