import os
from moviepy.editor import VideoFileClip
from django.conf import settings
from .models import Video, Movie
from gradio_client import Client

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

class EnglishLearningVideo:
    def __init__(self, video_instance, movie):
        self.video_instance = video_instance
        self.movie = movie
        self.complexity = get_complexity(video_instance.video.path)
        self.length = get_length(video_instance.video.path)
        self.audio_url = video_instance.video.path.replace(".mp4", ".wav")
        self.text = video_instance.video.path.replace(".mp4", ".txt")
        

    def extract_audio(self):
        if not os.path.exists(self.audio_url):
            video_clip = VideoFileClip(self.video_instance.video.path)  # Using video_path
            audio_clip = video_clip.audio
            audio_clip.write_audiofile(self.audio_url)  # Saves the audio file
            audio_clip.close()
            video_clip.close()

    def transcribe_audio(self):
        # Assuming an AI-based transcription method is available locally
        audio_url = self.audio_url
        if os.path.exists(self.text):
            print(f"Transcript already exists for {self.video_instance.video.path}")
            return self.text
        transcript_text = ai_model(audio_url)
        with open(self.video_instance.transcript_url, "w") as file:
            file.write(transcript_text)


def ai_model(audio_url):
    client = Client("https://openai-whisper.hf.space/")
    result = client.predict(audio_url, "transcribe")
    return result.get('prediction')


def populate_and_transcribe():
    base_dir = get_video_directory()
    for subdir in os.listdir(base_dir):
        video_dir = os.path.join(base_dir, subdir)
        for file_name in os.listdir(video_dir):
            if file_name.endswith(".mp4"):
                local_video_path = os.path.join(video_dir, file_name)
                movie, created = Movie.objects.get_or_create(title=subdir) 
                
                video_instance, created = Video.objects.get_or_create(
                    video=local_video_path,
                    movie=movie,
                    defaults={'complexity': get_complexity(local_video_path),
                              'length': get_length(local_video_path)}
                )

                video = EnglishLearningVideo(video_instance=video_instance, movie=movie)
                video.extract_audio()
                video.transcribe_audio()

                print(f"Processed {video_instance.video.path} for database insertion.")

