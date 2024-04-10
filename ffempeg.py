import subprocess
import os
import csv

def cut_video(input_file, output_file, start_time, end_time):
    command = f'ffmpeg -i "{input_file}" -ss {start_time} -to {end_time} -c copy "{output_file}"'
    subprocess.call(command, shell=True)

def get_video_with_captions(video_file, caption_file):
    video_file_translate = video_file[:-4].translate(str.maketrans('', '', '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'))
    output_dir = os.path.join("cut_videos", video_file_translate)
    os.makedirs(output_dir, exist_ok=True)

    with open(os.path.join('csv_important_text', caption_file), newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            start_time = row['Start Time']
            end_time = row['End Time']
            complexity = row['Complexity'].split('.')[0]  # Assuming complexity is a floating point number and you want the integer part
            intermediate_file = os.path.join(output_dir, f"{complexity}.mp4")
            output_file = os.path.join(output_dir, f"{complexity}_sub.mp4")
            cut_video(os.path.join('movies', video_file), intermediate_file, start_time, end_time)
            subprocess.run(["ffmpeg", "-i", intermediate_file, "-vf", f"subtitles='{os.path.join('csv_important_text', caption_file)}'", output_file])
            os.remove(intermediate_file)

def find_similarity(k, j):
    k_base = os.path.splitext(k)[0]
    j_base = os.path.splitext(j)[0]
    similarity = sum(1 for a, b in zip(k_base, j_base) if a == b)
    return similarity / max(len(k_base), len(j_base)) > 0.5

def find_subtitle(video_name):
    for subtitle_file in os.listdir("csv_important_text"):
        if find_similarity(video_name, subtitle_file):
            return subtitle_file

def get_video_and_subtitle():
    for video_name in os.listdir("movies"):
        subtitle_name = find_subtitle(video_name)
        if subtitle_name:
            print(f"Getting video cuts for {video_name} and {subtitle_name}")
            get_video_with_captions(video_name, subtitle_name)
        else:
            print(f"No matching subtitle found for {video_name}")

if __name__ == "__main__":
    get_video_and_subtitle()
