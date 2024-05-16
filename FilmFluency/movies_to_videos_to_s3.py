import nltk
nltk.download('punkt')


import argparse
import boto3
import ffmpeg
import pysrt
import uuid
from nltk.tokenize import word_tokenize, sent_tokenize
from learning.func import create_video_obj

def get_important_dialogue(srt_file_path):
    """Get important dialogue based on the complexity of the sentence and the length of the sentence."""
    subs = pysrt.open(srt_file_path)
    important_dialogue = []

    for sub in subs:
        sentences = sent_tokenize(sub.text)
        words = word_tokenize(sub.text)
        complexity = len(words) / len(sentences) if sentences else 0

        if len(words) > 10 and complexity > 10:
            important_dialogue.append(sub)

    return important_dialogue

def overwrite_srt_file(srt_file_path, important_dialogue):
    """Overwrite the subtitle file with important dialogue."""
    subs = pysrt.SubRipFile()
    for dialogue in important_dialogue:
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
    (
        ffmpeg
        .input(video_path, ss=start_time, to=end_time)
        .output(output_path, **{'c:v': 'libx264', 'c:a': 'aac'})
        .run()
    )
    return output_path

def upload_video_to_s3(video_path):
    """Upload the video to S3 of Digital Ocean."""
    s3 = boto3.client('s3', endpoint_url='https://nyc3.digitaloceanspaces.com')
    bucket_name = 'your-s3-bucket-name'
    s3.upload_file(video_path, bucket_name, video_path)
    return f"s3://{bucket_name}/{video_path}"

def video_to_db(video_path, transcript, movie, complexity):
    """Call Django function to save the video to the database."""
    create_video_obj(video_path, transcript, movie, complexity)

def main():
    parser = argparse.ArgumentParser(description='This is a script to convert movies to videos and upload them to S3')
    parser.add_argument('--movie', type=str, help='The name of the movie to convert to a video', required=True)
    parser.add_argument('--srt', type=str, help='The path to the transcript file', required=True)
    args = parser.parse_args()

    important_dialogue = get_important_dialogue(args.srt)
    overwrite_srt_file(args.srt, important_dialogue)
    video_paths = convert_movie_to_video(args.movie, args.srt)

    for video_path in video_paths:
        s3_video_url = upload_video_to_s3(video_path)
        video_to_db(s3_video_url, args.srt, args.movie, complexity='high')

if __name__ == '__main__':
    main()
