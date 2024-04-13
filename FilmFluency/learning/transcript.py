import os
from moviepy.editor import VideoFileClip
from gradio_client import Client
from .models import Video
from alibaba import get_oss_bucket
from django.conf import settings
import random


def get_complexity(video_path):
    return float(os.path.basename(video_path).split("_")[0])

def get_length(video_path):
    return VideoFileClip(video_path).duration


def get_video_directory():
    # Construct the path to the 'cut_videos' directory
    parent_dir = os.path.dirname(settings.BASE_DIR)
    video_dir = os.path.join(parent_dir, 'cut_videos')
    return video_dir

class EnglishLearningVideo:
    def __init__(self, video_url, movie, complexity, length):
        self.video_url = video_url
        self.movie = movie
        self.complexity = complexity
        self.length = length
        # Placeholder URLs; real URLs will be generated on demand
        self.transcript_url = self.video_url.replace(".mp4", ".txt")
        self.audio_url = self.video_url.replace(".mp4", ".wav")

    def get_random_signed_url(self, bucket, object_path):
        # Generate a random signed URL that expires after a specific short duration
        expiration_time = random.randint(300, 3600)  # Random expiration time between 5 minutes to 1 hour
        return bucket.sign_url('GET', object_path, expiration_time)

    def get_or_set_transcript(self, bucket):
        if not bucket.object_exists(self.transcript_url):
            self.set_transcript(bucket)
        return self.get_random_signed_url(bucket, self.transcript_url)

    def set_transcript(self, bucket):
        transcript = self.ai_model(self.get_random_signed_url(bucket, self.audio_url))
        bucket.put_object(self.transcript_url, transcript)
        
    def extract_audio(self, bucket):
        if not bucket.object_exists(self.audio_url):
            # Get the signed URL for the video to download or read directly into MoviePy
            video_url = self.get_random_signed_url(bucket, self.video_url)
            video_clip = VideoFileClip(video_url)  # Load video from a signed URL
            
            # Define the local audio file path properly using the basename of the video file
            local_audio_path = os.path.join(settings.BASE_DIR, f"{os.path.basename(self.video_url).replace('.mp4', '')}.wav")
            
            # Extract audio and save it locally
            audio_clip = video_clip.audio
            audio_clip.write_audiofile(local_audio_path)
            
            # Close clips to free resources
            audio_clip.close()
            video_clip.close()
            
            # Upload the audio file to the bucket
            bucket.put_object_from_file(self.audio_url, local_audio_path)

        # Return a new signed URL for the audio file
        return self.get_random_signed_url(bucket, self.audio_url)


    def ai_model(self, audio_url):
        client = Client("https://openai-whisper.hf.space/")
        result = client.predict(audio_url, "transcribe")
        return result.get('prediction')

def populate_and_transcribe():
    base_dir = get_video_directory()
    bucket = get_oss_bucket()

    for subdir in os.listdir(base_dir):
        video_dir = os.path.join(base_dir, subdir)
        for file in os.listdir(video_dir):
            if file.endswith(".mp4"):
                local_video_path = os.path.join(video_dir, file)
                oss_video_path = os.path.join(subdir, file)  # Adjust path as needed

                if not bucket.object_exists(oss_video_path):
                    bucket.put_object_from_file(oss_video_path, local_video_path)

                video = EnglishLearningVideo(
                    video_url=bucket.sign_url('GET', oss_video_path, 3600),
                    movie=subdir,
                    complexity=get_complexity(local_video_path),
                    length=get_length(local_video_path)
                )

                # Handle all components
                video.extract_audio(bucket)
                video.get_or_set_transcript(bucket)

                if not Video.objects.filter(video=video.video_url).exists():
                    Video.objects.create(video=video.video_url, complexity=video.complexity, movie=video.movie, length=video.length)
                    print(f"Inserted {video.video_url} into database")

def main():
    print("Starting to populate database and transcribe videos...")
    populate_and_transcribe()
    print("Completed all operations.")

if __name__ == "__main__":
    main()
