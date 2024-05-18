import os
from moviepy.editor import VideoFileClip
from .models import Video, Movie


def get_complexity(video_path):
    return float(os.path.basename(video_path).split("_")[0])

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

def create_video_obj(video_path, transcript_path, movie,thumbnail,audio, subtitle_path=""):
    """Create a Video object and save it to the database."""
    #take the first 3 words of the title of the movie and join them and search for the movie
    movie = movie.split()[:3].join()
    try:
        movie = Movie.objects.get(title__icontains=movie)
        video = Video.objects.create(
            movie=movie,
            video=video_path,
            transcript=transcript_path,
            subtitle=subtitle_path,
            audio=audio,
            thumbnail=thumbnail,
        )
    except Movie.DoesNotExist:
        with open('errors.txt', 'a') as f:
            f.write(f"Movie {movie} does not exist in the database.\n")
    except Exception as e:
        with open('errors.txt', 'a') as f:
            f.write(f"Error creating video object: {str(e)}\n")
    return video