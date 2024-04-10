import os 
import subprocess
from time import sleep
def download_movie(movie_name):
    subprocess.run(["pirate-get", movie_name, "-0"])
    


def getallmovies():
    movies = []
    for root, dirs, files in os.walk("cvs_important_text"):
        for file in files:
            file=file[:25]
            movies.append(file)
    return movies



print(getallmovies())
for movie in getallmovies():
    download_movie(movie)
    sleep(5)