# find_hardest_words , find_not_translated , fill_languages are functions that are used in the clipsmaker.py file.


# Path: FilmFluency/MovieToClips/find_word_translate.py

# find  the hardest words in the movie and translate them to the user's language
from django.db import transaction

import requests
import csv
from .models import Language, Translation
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
    existing_codes = set(Language.objects.values_list('tmdb_code', flat=True))
    new_languages = [Language(tmdb_code=code, name=name) for code, name in src_langs.items() if code not in existing_codes]
    
    with transaction.atomic():
        Language.objects.bulk_create(new_languages)
        print(f"Added {len(new_languages)} new languages.")



def load_word_frequencies():
    with open('word_frequency.csv', 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        return {row[0]: int(row[1]) for row in csv_reader if row}


def is_hard_word(words):
    """Return the lowest frequency word in the list."""
    lowest_frequency_word = None
    word_frequencies = load_word_frequencies()
    
    lowest_frequency = float('inf')

    for word in words:
        if word in word_frequencies and word_frequencies[word] < lowest_frequency:
            lowest_frequency = word_frequencies[word]
            lowest_frequency_word = word

    return lowest_frequency_word

def find_hardest_words():
    """Finds the hardest words in each movie translation and updates them."""
    languages = Language.objects.all()
    for language in languages:
        translations = Translation.objects.filter(language=language)
        for translation in translations:
            words = translation.translated_text.split()
            if not words:
                continue
            hardest_word = is_hard_word(words)
            if hardest_word:
                translated_word = translate_words(hardest_word, language.tmdb_code)
                translation.hardest_word = translated_word
                translation.save()

def translate_words(word, target_language):
    """Translate the given word to the given language using transformers."""
    try:
        input_text = f">>{target_language}<< {word}"
        input_ids = tokenizer.encode(input_text, return_tensors="pt")
        output_tokens = model.generate(input_ids)
        return tokenizer.decode(output_tokens[0], skip_special_tokens=True)
    except Exception as e:
        print(f"Error in translating word: {e}")
        return ""


def find_not_translated():
    """Finds the words that have not been translated yet."""
    # Get the list of languages
    languages = Language.objects.all()
    for language in languages:
        # Get the list of translations for the given language
        translations = Translation.objects.filter(language=language)
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
                

