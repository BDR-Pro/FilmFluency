import os
from moviepy.editor import VideoFileClip
import sqlite3
from gradio_client import Client

def make_table():
    with sqlite3.connect('english_learning.db') as conn:
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS EnglishLearningVideos (
                VideoPath TEXT,
                Complexity TEXT,
                Movie TEXT,
                Length REAL
            )
        ''')
        conn.commit()

class EnglishLearningVideo:
    def __init__(self, video_path):
        self.video = video_path
        self.movie = os.path.dirname(self.video).split("\\")[-1]
        self.complexity = self.video.split("\\")[-1].split("_")[0]
        self.length = VideoFileClip(self.video).duration

    def get_or_set_transcript(self):
        transcript_path = self.video.replace(".mp4", ".txt")
        try:
            with open(transcript_path, "r") as f:
                return f.read()  # Read the whole file as a single string
        except FileNotFoundError:
            return self.set_transcript()

    def set_transcript(self):
        transcript = ai_model(self.extract_audio())
        transcript_path = self.video.replace(".mp4", ".txt")
        with open(transcript_path, "w") as f:
            f.write(transcript)
        return transcript

    def extract_audio(self):
        if self.video.replace(".mp4", ".wav") in os.listdir():
            return self.video.replace(".mp4", ".wav")
        
        audio_path = self.video.replace(".mp4", ".wav")
        video_clip = VideoFileClip(self.video)
        audio_clip = video_clip.audio
        audio_clip.write_audiofile(audio_path)
        audio_clip.close()
        video_clip.close()
        return audio_path

def insert_video(video_path, complexity, movie, length):
    with sqlite3.connect('english_learning.db') as conn:
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO EnglishLearningVideos (VideoPath, Complexity, Movie, Length)
            VALUES (?, ?, ?, ?)
        ''', (video_path, complexity, movie, length))
        conn.commit()

def ai_model(audio_path):
    if not os.path.exists(audio_path):
        print("File does not exist:", audio_path)
        return
    if not audio_path.endswith(".wav"):
        print("Invalid file format:", audio_path)
        return
    client = Client("https://openai-whisper.hf.space/")
    result = client.predict(
                    audio_path,	# str (filepath or URL to file) in 'inputs' Audio component
                    "transcribe",	# str in 'Task' Radio component
                    api_name="/predict"
    )
    return result


def transcript():
    base_dir = "cut_videos"
    if not os.path.exists(base_dir):
        print("Directory does not exist:", base_dir)
        return
    for i in os.listdir(base_dir):
        video_dir = os.path.join(base_dir, i)
        for j in os.listdir(video_dir):
            if not j.endswith(".mp4"):
                continue
            video_path = os.path.join(video_dir, j)
            try:
                print(f"Transcribing {video_path}")
                video = EnglishLearningVideo(video_path)
                video.get_or_set_transcript()
                insert_video(video_path, video.complexity, video.movie, video.length)
                print("Stored transcript")
            except Exception as e:
                print(f"Failed to transcribe {video_path} with error {e}")

make_table()
transcript()
print("Transcribed all videos")
