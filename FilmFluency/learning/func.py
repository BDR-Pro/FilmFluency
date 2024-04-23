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
