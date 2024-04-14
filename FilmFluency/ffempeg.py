import subprocess
import os
import csv
import uuid
from time import sleep
from datetime import datetime, timedelta

parent_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(parent_dir)
    
csv_important_text = os.path.abspath("MovieToClips\\csv_important_text")
movies = os.path.abspath("MovieToClips\\movies")

def add_seconds(start_time, end_time):
    if type(start_time) not in [str] or type(end_time) not in [str]:
        return start_time, end_time
    try:
        start_dt = datetime.strptime(start_time, "%H:%M:%S")
        end_dt = datetime.strptime(end_time, "%H:%M:%S")
    except ValueError:
        return start_time, end_time
        
    if start_dt.second - end_dt.second < 5:
        end_dt = end_dt + timedelta(seconds=5)
    
    new_start_time = start_dt.strftime("%H:%M:%S")
    new_end_time = end_dt.strftime("%H:%M:%S")
    
    return new_start_time, new_end_time

def cut_video(input_file, output_file, start_time, end_time):
    command = f'ffmpeg  -i "{input_file}" -ss {start_time} -to {end_time} -c copy "{output_file}"'
    print(command)
    subprocess.call(command, shell=True)

def get_video_with_captions(video_file, caption_file):
    subtitle=os.path.join(csv_important_text, caption_file)
    video_file_translate = video_file[:-4].translate(str.maketrans('', '', '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'))
    output_dir = os.path.join("cut_videos", video_file_translate)
    os.makedirs(output_dir, exist_ok=True)

    with open(subtitle, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            text = row['Text']
            if len(text) < 10:
                continue
            start_time = row['Start Time']
            end_time = row['End Time']
            start_time , end_time = add_seconds(start_time,end_time)
            complexity = row['Complexity'].split('.')[0]
            uuid_str = str(uuid.uuid4())
            if not complexity.isdigit():
                continue
            intermediate_file = os.path.join(output_dir, f"{complexity}_{uuid_str}.mp4")
            output_file = os.path.join(output_dir, f"{complexity}_{uuid_str}_sub.mp4")
            print(f"Cutting video from {start_time} to {end_time} with complexity {complexity}")
            cut_video(os.path.join(movies, video_file), intermediate_file, start_time, end_time)

def find_similarity(k, j):
    k_base = os.path.splitext(k)[0].translate(str.maketrans('', '', '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'))
    j_base = os.path.splitext(j)[0].translate(str.maketrans('', '', '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'))
    similarity = sum(1 for a, b in zip(k_base, j_base) if a == b)
    return similarity / max(len(k_base), len(j_base)) > 0.3

def find_subtitle(video_name):
    for subtitle_file in os.listdir("csv_important_text"):
        if find_similarity(video_name, subtitle_file):
            return subtitle_file

def get_video_and_subtitle():
    for video_name in os.listdir(movies):
        subtitle_name = find_subtitle(video_name)
        if subtitle_name:
            print(f"Getting video cuts for {video_name} and {subtitle_name}")
            get_video_with_captions(video_name, subtitle_name)
            os.remove(os.path.join(csv_important_text, subtitle_name))
            os.remove(os.path.join(movies, video_name))
        
        else:
            print(f"No matching subtitle found for {video_name}")


if __name__ == "__main__":
    get_video_and_subtitle()
