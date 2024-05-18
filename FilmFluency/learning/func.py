language_to_country_mapping = {
    'en': 'US',  # English to USA
    'es': 'ES',  # Spanish to Spain
    'fr': 'FR',  # French to France
    'de': 'DE',  # German to Germany
    'ar': 'SA',  # Arabic to Saudi Arabia
    'zh': 'CN',  # Chinese to China
    'ru': 'RU',  # Russian to Russia
    'ja': 'JP',  # Japanese to Japan
    'pt': 'PT',  # Portuguese to Portugal
    'it': 'IT',  # Italian to Italy
    'ko': 'KR',  # Korean to South Korea
    'nl': 'NL',  # Dutch to Netherlands
    'sv': 'SE',  # Swedish to Sweden
    'pl': 'PL',  # Polish to Poland
    'tr': 'TR',  # Turkish to Turkey
    'th': 'TH',  # Thai to Thailand
    'cs': 'CZ',  # Czech to Czech Republic
    'el': 'GR',  # Greek to Greece
    'hi': 'IN',  # Hindi to India
    'he': 'IL',  # Hebrew to Israel
    'da': 'DK',  # Danish to Denmark
    'fi': 'FI',  # Finnish to Finland
    'no': 'NO',  # Norwegian to Norway
    'hu': 'HU',  # Hungarian to Hungary
    'id': 'ID',  # Indonesian to Indonesia
    # Add more mappings as needed
}

def language_to_country(language_code):
    """ Map language code to country code. """
    return language_to_country_mapping.get(language_code, 'US')


from .models import Video, Movie
def create_video_obj(video_path, transcript_path, movie,thumbnail, subtitle_path=""):
    """Create a Video object and save it to the database."""
    #take the first 3 words of the title of the movie and join them and search for the movie
    movie = movie.split()[:3].join()
    try:
        movie = Movie.objects.get(title__icontains=movie)
        video = Video.objects.create(
            movie=movie,
            video=video_path,
            transcript=transcript_path,
            subtitle=subtitle_path,
            thumbnail=thumbnail,
        )
    except Movie.DoesNotExist:
        with open('errors.txt', 'a') as f:
            f.write(f"Movie {movie} does not exist in the database.\n")
    except Exception as e:
        with open('errors.txt', 'a') as f:
            f.write(f"Error creating video object: {str(e)}\n")
    return video