import re
import os

def clean_files():
    for filename in os.listdir("csv_important_text"):
        file_path = os.path.join("csv_important_text", filename)
        with open(file_path, 'r', encoding='utf-8') as file:
            # Read the file content and join it into a single string
            file_content = ''.join(file.readlines())
            
            # Remove standalone numbers not part of times or decimals
            pattern = r"(?<![:.\d])\d+(?![.:\d])"
            modified_text = re.sub(pattern, "", file_content)
            
            # Remove one of duplicate commas
            modified_text = re.sub(r',,', ',', modified_text)
            
            # Remove a comma if there's nothing on the right of it
            modified_text = re.sub(r',\s*$', '', modified_text)

        # Write the modified content back to the file
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(modified_text)

