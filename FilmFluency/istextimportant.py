import re
from textstat.textstat import textstat
from tqdm import tqdm
import os


def text_to_csv(useful_sentences,srt_file_name):
    if len(useful_sentences)<4:
        return
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(parent_dir)
    
    srt_file_name= srt_file_name.split("\\")[-1].replace(".srt",".csv")
    path_file = os.path.join("MovieToClips\\csv_important_text",srt_file_name)
    with open(path_file, 'w', encoding='utf-8') as file:
        file.write("Text,Complexity,Start Time,End Time\n")
        for sentence in useful_sentences:
            file.write(f"{sentence[0]},{sentence[1]},{sentence[2]},{sentence[3]}\n")

def return_text_from_srt(srt_file_name):
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join("MovieToClips\\srt", srt_file_name)
    with open(file_path, 'r', encoding='utf-8') as file:
            srt_file_text = file.read()
    return srt_file_text
        
def process_srt_file(srt_text,srt_file_name):
    """
    Process the text of an SRT file, extracting sentences and their timings,
    focusing on sentences that might be useful for learning English.
    
    Args:
    srt_text (str): The text of the SRT file.
    
    Returns:
    list of tuples: Each tuple contains the sentence and its start time.
    """
  
    
    
    blocks = re.split(r'\n\n', srt_text)
    
    
    time_pattern = re.compile(r'(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})')
    text_pattern = re.compile(r'\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}\n(.+)', re.DOTALL)
    
    useful_sentences = []
    with tqdm(total=len(blocks) , desc=f"Srt of{srt_file_name}") as pbar:
        for block in blocks:
            time_match = time_pattern.search(block)
            text_match = text_pattern.search(block)
            
            if time_match and text_match:
                
                start_time = time_match.group(1).split(',')[0]
                text = text_match.group(1).replace('\n', ' ')  
                end_time = time_match.group(2).split(',')[0]
                
                
                complexity = textstat.flesch_reading_ease(text)
                
                if complexity < 45 and complexity > 0:  
                    text=text.translate(str.maketrans('', '', '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'))
                    useful_sentences.append((text,complexity, start_time, end_time))
            pbar.update(1)
        
        return useful_sentences



        
def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    with tqdm(total=len(os.listdir("MovieToClips\\srt")), desc="Srt Files") as pbar:
        for i in os.listdir("MovieToClips\\srt"):
            srt_file_name = os.path.join("MovieToClips\\srt", i)
            if i in os.listdir("MovieToClips\\csv_important_text"):
                pbar.update(1)
                continue
            srt_file_text = return_text_from_srt(i)
            useful_sentences = process_srt_file(srt_file_text, srt_file_name)
            text_to_csv(useful_sentences,srt_file_name)
            pbar.update(1)
            
    print("All SRT files processed")    
    
