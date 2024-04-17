import subprocess
import os
import csv
import boto3
from botocore.client import Config
import uuid
from upload_to_s3 import upload_to_s3
from datetime import datetime, timedelta
from load_env import load_env
import string
load_env()
parent_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(parent_dir)

csv_important_text = os.path.join("MovieToClips", "csv_important_text")
movies = os.path.join("MovieToClips", "movies")

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

def cut_video(input_file, output_file, start_time, end_time):
    command = f'ffmpeg -i "{input_file}" -ss {start_time} -to {end_time} -c copy "{output_file}"'
    subprocess.call(command, shell=True)

def find_similarity(k, j):
    k_base = os.path.splitext(k)[0].translate(str.maketrans('', '', string.punctuation))
    j_base = os.path.splitext(j)[0].translate(str.maketrans('', '', string.punctuation))
    similarity = sum(1 for a, b in zip(k_base, j_base) if a == b)
    return similarity / max(len(k_base), len(j_base)) > 0.3

def find_subtitle(video_name):
    for subtitle_file in os.listdir(csv_important_text):
        if find_similarity(video_name, subtitle_file):
            return subtitle_file


def get_video_and_subtitle():
    for video_name in os.listdir(movies):
        subtitle_name = find_subtitle(video_name)
        if subtitle_name:
            print(f"Getting video cuts for {video_name} and {subtitle_name}")
            video_path = os.path.join(movies, video_name)
            subtitle_path = os.path.join(csv_important_text, subtitle_name)
            with open(subtitle_path, 'r') as f:
                reader = csv.reader(f)
                for i, row in enumerate(reader):
                    if i == 0:
                        continue
                    start_time, end_time = add_seconds(row[0], row[1])
                    cut_video(video_path, video_path.replace('.mp4', '_cut.mp4'), start_time, end_time)
                    upload_to_s3(subtitle_path, video_name)
                    os.remove(video_path)
                    os.remove(subtitle_path)
                    break
        else:
            print(f"No matching subtitle found for {video_name}")

if __name__ == "__main__":
    get_video_and_subtitle()
