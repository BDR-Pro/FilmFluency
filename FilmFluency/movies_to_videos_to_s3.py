import nltk
nltk.download('punkt')


import argparse
from api.upload_to_s3 import upload_to_s3 
import ffmpeg
import pysrt
import uuid
from nltk.tokenize import word_tokenize
from learning.func import create_video_obj
from datetime import datetime, timedelta
import textstat


def add_seconds(start_time, end_time):
    if type(start_time) not in [str] or type(end_time) not in [str]:
        return start_time, end_time
    try:
        start_dt = datetime.strptime(start_time, "%H:%M:%S")
        end_dt = datetime.strptime(end_time, "%H:%M:%S")
    except ValueError:
        return start_time, end_time
        
    if end_dt.second - start_dt.second < 5:
        end_dt = end_dt + timedelta(seconds=5)
    
    new_start_time = start_dt.strftime("%H:%M:%S")
    new_end_time = end_dt.strftime("%H:%M:%S")
    
    return new_start_time, new_end_time

def get_complexity(sentence):
    return  textstat.flesch_reading_ease(sentence) 

def get_important_dialogue(srt_file_path):
    """Get important dialogue based on the complexity of the sentence and the length of the sentence."""
    subs = pysrt.open(srt_file_path)
    important_dialogue = {}

    for sub in subs:
        
        words = word_tokenize(sub.text)
        
        if len(words) < 5:
            continue
        
        complexity = get_complexity(sub.text)

        if complexity > 10:
            important_dialogue[sub] = complexity

    return important_dialogue

def overwrite_srt_file(srt_file_path, important_dialogue):
    """Overwrite the subtitle file with important dialogue."""
    subs = pysrt.SubRipFile()
    for dialogue in important_dialogue.keys():
        subs.append(dialogue)
    subs.save(srt_file_path, encoding='utf-8')

def convert_movie_to_video(movie, srt_file_path):
    """Convert the movie to videos based on the srt file and save them to the hard drive."""
    subs = pysrt.open(srt_file_path)
    video_paths = []

    for sub in subs:
        start_time = sub.start.to_time()
        end_time = sub.end.to_time()
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
    
    start_time , end_time = add_seconds(start_time,end_time)
    
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

def video_to_db(video_path, transcript, movie, complexity):
    """Call Django function to save the video to the database."""
    create_video_obj(video_path, transcript, movie, complexity)

def video_processing(movie, important_dialogue, srt):
    video_paths = convert_movie_to_video(movie, srt)

    for video_path in video_paths:
        complexity = important_dialogue.get(video_path)
        s3_video_url = upload_to_s3(video_path, f"videos/{movie}/{uuid.uuid4()}.mp4")
        thumbnail =  upload_to_s3(screenshot_video(video_path),f"thumbnail/{movie}.webp")
        video_to_db(s3_video_url, srt, movie, complexity=complexity,thumbnail=thumbnail)


def main():
    parser = argparse.ArgumentParser(description='This is a script to convert movies to videos and upload them to S3')
    parser.add_argument('--movie', type=str, help='The name of the movie to convert to a video', required=True)
    parser.add_argument('--srt', type=str, help='The path to the transcript file', required=True)
    args = parser.parse_args()

    important_dialogue = get_important_dialogue(args.srt)
    overwrite_srt_file(args.srt, important_dialogue)

    video_processing(args.movie, important_dialogue, args.srt)

if __name__ == '__main__':
    main()
