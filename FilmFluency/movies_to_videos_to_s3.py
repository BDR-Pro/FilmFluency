import os
import django

# Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FilmFluency.settings')
django.setup()

import csv
import re
import argparse
import uuid
import ffmpeg
import textstat
import nltk
from datetime import datetime, timedelta
from api.upload_to_s3 import upload_to_s3
from learning.transcript import create_video_obj , does_movie_exist
from moviepy.editor import VideoFileClip
# Download nltk data
nltk.download('punkt')


def get_length(video_path):
    return VideoFileClip(video_path).duration


def parse_srt(srt_file_path):
    """Parse the SRT file using regex to extract the subtitles."""
    encodings = ['utf-8', 'latin-1', 'utf-16', 'utf-32', 'utf-16-le', 'utf-16-be', 'utf-32-le', 'utf-32-be']
    for i in encodings:
        try:
            with open(srt_file_path, 'r', encoding=i) as file:
                srt_content = file.read()
                break
        except:
            continue

    pattern = re.compile(
        r'(\d+)\n'
        r'(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n'
        r'((?:.*\n)+?)\n',
        re.MULTILINE
    )

    subtitles = []
    for match in pattern.finditer(srt_content):
        index = int(match.group(1))
        start_time = match.group(2).replace(',', '.')
        end_time = match.group(3).replace(',', '.')
        text = match.group(4).replace('\n', ' ').strip()
        subtitles.append((index, start_time, end_time, text))

    return subtitles

def get_important_dialogue(subtitles):
    """Get important dialogue based on the complexity of the sentence and the length of the sentence."""
    important_dialogue = []

    for index, start_time, end_time, text in subtitles:
        words = nltk.word_tokenize(text)
        
        if len(words) < 5:
            continue
        
        complexity = get_complexity(text)

        if complexity < 50:  # Flesch Reading Ease score less than 60
            important_dialogue.append({
                'complexity': complexity,
                'start_time': start_time,
                'end_time': end_time,
                'sentence': text
            })

    return important_dialogue

def save_to_csv(srt_file_path, important_dialogue):
    """Save important dialogue to a CSV file with the same path and name as the SRT file."""
    csv_file_path = srt_file_path.replace('.srt', '.csv')
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['complexity', 'start_time', 'end_time', 'sentence']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for dialogue in important_dialogue:
            writer.writerow(dialogue)

def get_complexity(sentence):
    return textstat.flesch_reading_ease(sentence)

def add_seconds(start_time, end_time):
    try:
        start_dt = datetime.strptime(start_time, "%H:%M:%S,%f")
        end_dt = datetime.strptime(end_time, "%H:%M:%S,%f")
    except ValueError:
        return start_time, end_time
        
    if end_dt.second - start_dt.second < 5:
        end_dt = end_dt + timedelta(seconds=5)
    
    new_start_time = start_dt.strftime("%H:%M:%S")
    new_end_time = end_dt.strftime("%H:%M:%S")
    
    return new_start_time, new_end_time

def convert_movie_to_video(movie, important_dialogue):
    """Convert the movie to videos based on the important dialogue and save them to the hard drive."""
    video_paths = []

    for dialogue in important_dialogue:
        start_time = dialogue['start_time']
        end_time = dialogue['end_time']
        output_path = f"{uuid.uuid4()}.mp4"
        
        (
            ffmpeg
            .input(movie, ss=start_time, to=end_time)
            .output(output_path, **{'c:v': 'libx264', 'c:a': 'aac'})
            .run()
        )
        video_paths.append(output_path)

    return video_paths

def cut_video(video_path, start_time, end_time):
    """Cut the video based on start time and end time using ffmpeg."""
    output_path = f"{uuid.uuid4()}.mp4"
    
    start_time , end_time = add_seconds(start_time, end_time)
    
    (
        ffmpeg
        .input(video_path, ss=start_time, to=end_time)
        .output(output_path, **{'c:v': 'libx264', 'c:a': 'aac'})
        .run()
    )
    return output_path

def screenshot_video(video_path):
    """Take a screenshot of the video at a 2s and convert it to a jpg format."""
    output_path = f"{uuid.uuid4()}.jpg"

    try:
        (
            ffmpeg
            .input(video_path, ss=2)
            .output(output_path, vframes=1, format='webp')
            .run()
        )
    except ffmpeg.Error as e:
        print(f"WebP format failed, using JPG format instead. Error: {e}")
        output_path = f"{uuid.uuid4()}.jpg"
        (
            ffmpeg
            .input(video_path, ss=2)
            .output(output_path, vframes=1, format='mjpeg')
            .run()
        )

    return output_path if file_greater_than_zero(output_path) else None


def file_greater_than_zero(file_path): 
    return os.path.getsize(file_path) > 0


def video_to_audio(video_path):
    """Convert the video to audio using ffmpeg."""
    output_path = f"{uuid.uuid4()}.wav"

    (
        ffmpeg
        .input(video_path)
        .output(output_path, **{'c:a': 'pcm_s16le'})
        .run()
    )
    return output_path


def filter_dialogue(line):
    """Filter out non-dialogue lines from the subtitle content."""
    # Regex pattern to match lines representing non-dialogue sounds or actions
    non_dialogue_pattern = re.compile(r'^\[.*\]$')
    
    # Check if the line matches the non-dialogue pattern
    if non_dialogue_pattern.match(line) or not line.strip():
        return None
    return line.strip()

def video_to_db(video_path, transcript, movie, complexity, thumbnail, audio, length):
    """Call Django function to save the video to the database."""
    create_video_obj(video_path, transcript, movie, thumbnail, audio, complexity, length)

def video_processing(movie, important_dialogue, slug):
    video_paths = convert_movie_to_video(movie, important_dialogue)
    movie = movie.split('\\')[-1]
    movie = movie.replace('.mp4', '')
    movie = " ".join(movie.split()[:3])
    for idx, video_path in enumerate(video_paths):
        dialogue = important_dialogue[idx]
        complexity = dialogue['complexity']
        if not filter_dialogue(dialogue['sentence']):
            continue
        video_s3=f"videos/{movie}/{uuid.uuid4()}.mp4"
        upload_to_s3(video_path, video_s3)
        length = get_length(video_path)
        path=screenshot_video(video_path)
        if path:
            file_name = path.split('\\')[-1]
            thumbnail_in_s3 = f"thumbnails/{movie}/{file_name}"
            upload_to_s3(path, thumbnail_in_s3)
        audio_in_s3 = f"audio/{movie}/{uuid.uuid4()}.wav"
        upload_to_s3(video_to_audio(video_path), audio_in_s3)
        video_to_db(video_s3, dialogue['sentence'], slug, complexity, thumbnail_in_s3, audio_in_s3, length)

def main():
    parser = argparse.ArgumentParser(description='This is a script to convert movies to videos and upload them to S3')
    parser.add_argument('--movie', type=str, help='The name of the movie to convert to a video', required=True)
    parser.add_argument('--srt', type=str, help='The path to the transcript file', required=True)
    parser.add_argument('--id', type=str, help='The id of The Movie in DB', required=True)
    
    args = parser.parse_args()
    if not does_movie_exist(args.id):
        print("Movie does not exist in the directory.")
        return
    subtitles = parse_srt(args.srt)
    important_dialogue = get_important_dialogue(subtitles)
    save_to_csv(args.srt, important_dialogue)

    video_processing(args.movie, important_dialogue, args.id)

if __name__ == '__main__':
    main()
