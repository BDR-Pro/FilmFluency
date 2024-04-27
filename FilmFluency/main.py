"""VideoMaker module main file.

This module handles the retrieval and processing of movies to ensure they have
appropriate subtitles and transcripts, then uploads these to AWS S3.
"""

from learning.isitalreadydownloaded import getAllMoviesWithoutSubtitleOrTranscript, edit_movie
from api.upload_to_s3 import upload_to_s3
import subprocess
def download_movie(movie):
    """Download the movie's subtitles and transcripts, then upload them to AWS S3."""
    
def main():
    """Main function to process all movies that require subtitles or transcripts."""
    print("Starting the Subtitle and transcript upload to s3 process")
    movies = getAllMoviesWithoutSubtitleOrTranscript()
    for index, movie in enumerate(movies):
        print(f"Completion: {index}/{len(movies)} movies processed")
        print(f"{index/len(movies)*100:.2f}% complete")
        print(f"Processing movie: {movie.title}")
        
        download_movie(movie)
        

if __name__ == "__main__":
    main()
    #fix_erorrs()
