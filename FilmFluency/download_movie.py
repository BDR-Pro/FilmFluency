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

def fonud_similiraty(movie1,movie2):
    similarity = 0
    for i in range(len(movie1)):
        if movie1[i] == movie2[i]:
            similarity += 1
    return True if similarity/len(movie1) > 0.8 else False

def is_dublicated(movies):
    #search for dublicated movies in os.listdir("movies") with 80% similarity
    dublicated_movies = []
    for movie in movies:
        for file in os.listdir("movies"):
            if fonud_similiraty(movie,file) in file:
                dublicated_movies.append(movie)
    for movie in dublicated_movies:
        movies.remove(movie)
    return movies
    


def main():
    print("Downloading movies")
    list_=getallmovies()

    list_ = is_dublicated(list_)

    for movie in list_:
        print(f"Downloading {movie}")
        download_movie(movie)
        sleep(5)