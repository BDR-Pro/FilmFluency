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
from learning.transcript import create_video_obj


# Download nltk data
nltk.download('punkt')

def parse_srt(srt_file_path):
    """Parse the SRT file using regex to extract the subtitles."""
    with open(srt_file_path, 'r', encoding='utf-8') as file:
        srt_content = file.read()

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

        if complexity < 60:  # Flesch Reading Ease score less than 60
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
    """Take a screenshot of the video at a 2s and convert it to a webp format."""
    output_path = f"{uuid.uuid4()}.jpg"

    (
        ffmpeg
        .input(video_path, ss=2)
        .output(output_path, vframes=1, format='webp')
        .run()
        
    )
    return output_path

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

def video_to_db(video_path, transcript, movie, complexity, thumbnail, audio):
    """Call Django function to save the video to the database."""
    create_video_obj(video_path, transcript, movie, complexity, thumbnail, audio)

def video_processing(movie, important_dialogue):
    video_paths = convert_movie_to_video(movie, important_dialogue)
    movie = movie.split('\\')[-1]
    movie = movie.replace('.mp4', '')
    movie = " ".join(movie.split()[:3])
    for idx, video_path in enumerate(video_paths):
        dialogue = important_dialogue[idx]
        complexity = dialogue['complexity']
        s3_video_url = upload_to_s3(video_path, f"videos/{movie}/{uuid.uuid4()}.mp4")
        thumbnail = upload_to_s3(screenshot_video(video_path), f"thumbnail/{movie}.webp")
        audio = upload_to_s3(video_to_audio(video_path), f"audio/{movie}/{uuid.uuid4()}.wav")
        video_to_db(s3_video_url, dialogue['sentence'], movie, complexity, thumbnail, audio)

def main():
    parser = argparse.ArgumentParser(description='This is a script to convert movies to videos and upload them to S3')
    parser.add_argument('--movie', type=str, help='The name of the movie to convert to a video', required=True)
    parser.add_argument('--srt', type=str, help='The path to the transcript file', required=True)
    args = parser.parse_args()

    subtitles = parse_srt(args.srt)
    important_dialogue = get_important_dialogue(subtitles)
    save_to_csv(args.srt, important_dialogue)

    video_processing(args.movie, important_dialogue)

if __name__ == '__main__':
    main()
