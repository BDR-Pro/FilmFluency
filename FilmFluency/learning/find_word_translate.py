# find_hardest_words , find_not_translated , fill_languages are functions that are used in the clipsmaker.py file.


# Path: FilmFluency/MovieToClips/find_word_translate.py

# find  the hardest words in the movie and translate them to the user's language

import requests
import csv
from .models import Language, translation
import requests
import json
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
tokenizer = AutoTokenizer.from_pretrained("google/madlad400-10b-mt")
model = AutoModelForSeq2SeqLM.from_pretrained("google/madlad400-10b-mt")

src_langs = {
    "en": "English",
    "fr": "French",
    "ar": "Arabic",
    "zh": "Mandarin Chinese",
    "es": "Spanish",
    "hi": "Hindi",
    "bn": "Bengali",
    "pt": "Portuguese",
    "ru": "Russian",
    "ja": "Japanese",
    "de": "German"
}

def fill_languages():
    for src_lang_code, src_lang_name in src_langs.items():
        # Check if the language already exists in the database
        if not Language.objects.filter(code=src_lang_code).exists():
            # Create a new Language object
            language = Language.objects.create(tmdb_code=src_lang_code, name=src_lang_name)
            language.save()
            print(f"Added language: {src_lang_name} ({src_lang_code})")
        else:
            print(f"Language already exists: {src_lang_name} ({src_lang_code})")


def is_hard_word(words):
    """Return the lowest frequency word in the list."""
    csv_file = open('word_frequency.csv', 'r')
    csv_reader = csv.reader(csv_file)
    lowest_frequency = {'word': '', 'frequency': 1000000}
    for word in words:
        for row in csv_reader:
            if word == row[0]:
                frequency = row[1]
                if frequency < lowest_frequency['frequency']:
                    lowest_frequency['word'] = word
                    lowest_frequency['frequency'] = frequency
            break
        if word.isalpha() and word not in lowest_frequency:
            lowest_frequency['word'] = word
            lowest_frequency['frequency'] = 0
         
    return lowest_frequency['word']
        

def translate_words(words, language):
    """Translate the given words to the given language using transformers"""
    
    input_text = f">>{language}<< {words}"
    input_ids = tokenizer.encode(input_text, return_tensors="pt")

    # Generate translation
    output_tokens = model.generate(input_ids)

    # Decode the translation
    translated_text = tokenizer.decode(output_tokens[0], skip_special_tokens=True)
    return translated_text

def find_hardest_words():
    """Finds the hardest words in the movie and translates them to the user's language."""
    # Get the list of languages
    languages = Language.objects.all()
    for language in languages:
        # Get the list of translations for the given language
        translations = translation.objects.filter(language=language)
        for translation in translations:
            # Get the translated text
            translated_text = translation.translated_text
            # Split the text into words
            words = translated_text.split()
            if language.tmdb_code=="en":
                hardest_words = is_hard_word(words)
            # Translate the hardest words to the user's language
            translated_words = translate_words(hardest_words, language.tmdb_code)
            # Save the translated words to the database
            translation.hardest_word = translated_words
            translation.save()

def find_not_translated():
    """Finds the words that have not been translated yet."""
    # Get the list of languages
    languages = Language.objects.all()
    for language in languages:
        # Get the list of translations for the given language
        translations = translation.objects.filter(language=language)
        for translation in translations:
            # Check if the translation is empty
            if not translation.translated_text:
                # Get the original text
                original_text = translation.original_text
                # Save the original text as the translation
                translation.translated_text = original_text
                if language.tmdb_code=="en":
                    translation.hardest_word = find_hardest_words(original_text)
                translation.save()
                print(f"Translation for {original_text} not found. Saved the original text as the translation.")  
                

