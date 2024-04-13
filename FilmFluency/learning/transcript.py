import os
from moviepy.editor import VideoFileClip
from gradio_client import Client
from .models import Video

from django.conf import settings

def get_video_directory():
    # Construct the path to the 'cut_videos' directory
    parent_dir = os.path.dirname(settings.BASE_DIR)
    video_dir = os.path.join(parent_dir, 'cut_videos')
    return video_dir

class EnglishLearningVideo:
    def __init__(self, video_path):
        self.video = video_path
        self.movie = os.path.basename(os.path.dirname(self.video))
        self.complexity = float(os.path.basename(self.video).split("_")[0])
        self.length = VideoFileClip(self.video).duration

    def get_or_set_transcript(self):
        transcript_path = self.video.replace(".mp4", ".txt")
        if os.path.exists(transcript_path):
            with open(transcript_path, "r") as f:
                return f.read()
        else:
            return self.set_transcript()

    def set_transcript(self):
        audio_path = self.extract_audio()
        transcript = self.ai_model(audio_path)
        with open(self.video.replace(".mp4", ".txt"), "w") as f:
            f.write(transcript)
        return transcript

    def extract_audio(self):
        audio_path = self.video.replace(".mp4", ".wav")
        if not os.path.exists(audio_path):
            video_clip = VideoFileClip(self.video)
            audio_clip = video_clip.audio
            audio_clip.write_audiofile(audio_path)
            audio_clip.close()
            video_clip.close()
        return audio_path

    def ai_model(self, audio_path):
        client = Client("https://openai-whisper.hf.space/")
        result = client.predict(audio_path, "transcribe")
        return result.get('prediction')

def populate_and_transcribe():
    base_dir = get_video_directory()
    for subdir in os.listdir(base_dir):
        video_dir = os.path.join(base_dir, subdir)
        for file in os.listdir(video_dir):
            if file.endswith(".mp4"):
                video_path = os.path.join(video_dir, file)
                video = EnglishLearningVideo(video_path)
                video.get_or_set_transcript()
                if not Video.objects.filter(video=video_path).exists():
                    Video.objects.create(video=video_path, complexity=video.complexity, movie=video.movie, length=video.length)
                    print(f"Inserted {video_path} into database")

def main():
    print("Starting to populate database and transcribe videos...")
    populate_and_transcribe()
    print("Completed all operations.")

if __name__ == "__main__":
    main()
