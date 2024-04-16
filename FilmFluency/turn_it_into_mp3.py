import os
import subprocess

def remove_and_rename(input_file, output_file):
    """Remove the input file and rename the output file to the original name."""
    os.remove(input_file)
    os.rename(output_file, input_file)

def get_audio_codec(file_path):
    """Use ffprobe to get the audio codec of the given video file."""
    cmd = [
        'ffprobe',
        '-v', 'error',
        '-select_streams', 'a:0',  # Select the first audio stream
        '-show_entries', 'stream=codec_name',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        file_path
    ]
    try:
        codec = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode().strip()
        return codec
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while checking codec: {e.output.decode()}")
        return None


def convert_to_mp3(input_file):
    """Convert the audio stream of the input file to mp3 using ffmpeg."""
    output_file = input_file.rsplit('.', 1)[0] + "_mp3.mp4"  # Assuming the file extension is .mp4
    cmd = [
        'ffmpeg',
        '-i', input_file,
        '-vcodec', 'libx264',  # Set video codec to 'H.264/AVC
        '-acodec', 'libmp3lame',  # Set audio codec to 
        '-strict', 'experimental',
        output_file,
        '-y'  # Overwrite output file if it exists
    ]
    try:
        subprocess.run(cmd, check=True)
        print(f"Converted {input_file} to Mp3 successfully. New file: {output_file}")
        remove_and_rename(input_file, output_file)
    except subprocess.CalledProcessError as e:
        print(f"Failed to convert {input_file}: {str(e)}")


def process_directory(directory):
    """Process each video file in the specified directory."""
  
    for root, dirs, files in os.walk(directory):
        for file in files:
            if os.path.isdir(file):
                process_directory(file)
            if file.endswith(('.mp4', '.mkv', '.avi')):  # Add other video formats as needed
                print(f"Processing: {file}")
                file_path = os.path.join(root, file)
                codec = get_audio_codec(file_path)
                if codec != 'libmp3lame':
                    convert_to_mp3(file_path)


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    os.chdir("MovieToClips")
    process_directory("cut_videos")
    