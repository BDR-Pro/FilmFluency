import os
import subprocess

def download_movie(movie_name):
    # Replace spaces in movie name with underscores
    movie_name = movie_name.replace(" ", "_")

    # Construct the torrent search command
    search_command = f"python -m bittorrent_cli search {movie_name}"

    # Execute the search command and get the output
    search_output = subprocess.check_output(search_command, shell=True).decode("utf-8")

    # Extract the magnet link from the search output
    magnet_link = search_output.splitlines()[0].split(" ")[1]
    # Construct the download command
    
    download_command = f"C:\Users\Public\Desktop\qBittorrent.lnk --add-torrent={magnet_link}"

    # Execute the download command
    subprocess.call(download_command, shell=True)

# Example usage
movie_name = input("Enter the movie name: ")
download_movie(movie_name)