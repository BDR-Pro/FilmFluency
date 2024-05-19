import os
from moviepy.editor import VideoFileClip
from .models import Video, Movie
import sys
def does_movie_exist(id):
    """Check if the movie exists in the database."""
    try:
        movie=Movie.objects.get(id=id)
        print(movie)
        return True
    except Movie.DoesNotExist:
        sys.exit("Movie does not exist in the database.")


def get_length(video_path):
    return VideoFileClip(video_path).duration

def get_video_directory():
    # Construct the path to the 'cut_videos' directory
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    parent = os.path.dirname(curr_dir)
    media_dir = os.path.join(parent, 'MovieToClips')
    video_dir = os.path.join(media_dir, 'cut_videos')
    print(video_dir)
    print(os.path.exists(video_dir))
    return video_dir

def create_video_obj(video_path, transcript_path, id ,thumbnail,audio,complexity,length):
    """Create a Video object and save it to the database."""
    movie = Movie.objects.get(id=id)
    video = Video.objects.create(
        movie=movie,
        video=video_path,
        text=transcript_path,
        length=length,
        complexity=complexity,
        audio=audio,
        thumbnail=thumbnail,
    )

def get_length_video(video_path):
    return VideoFileClip(video_path).duration