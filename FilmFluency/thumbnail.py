import os 

def get_thumbnail(video_file):
    """ Generate a thumbnail image from a video file. """
    output_thumbnail = video_file.replace(".mp4", ".jpg")
    command = f'ffmpeg -i "{video_file}" -ss 00:00:01.000 -vframes 1 {output_thumbnail}""'
    os.system(command)



def file_exists(filepath):
    return os.path.exists(filepath)

def get_all_videos():
    """ Return all videos in cut_videos directory. """
    videos = []
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    os.chdir("MovieToClips")
    for root, dirs, files in os.walk("cut_videos"):
        for file in files:
            video_file = os.path.join(root, file)
            if video_file.endswith(".mp4") and not file_exists(video_file.replace(".mp4", ".jpg")):
                print(f"Found video file: {video_file}")
                videos.append(video_file)
    print(f"{len(videos)} videos found in cut_videos directory.")
    return videos


def main():
    videos = get_all_videos()
    for video in videos:
        get_thumbnail(video)
    
    print("All thumbnails generated successfully.")
    
if __name__ == "__main__":
    main()