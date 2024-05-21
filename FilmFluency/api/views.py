from django.http import JsonResponse
from api.upload_to_s3 import serve_secure_media
from api.decorators import check_paid_user
from learning.models import Movie
import requests
from django.conf import settings
from api.upload_to_s3 import upload_to_s3
from api.func import is_it_a_valid_imdb_id, get_movie_data_from_tmdb

@check_paid_user
def secure_media_view(request, file_key):
    print(f"{file_key=}")
    url = serve_secure_media(file_key)
    return JsonResponse({'url': url})


def search_suggestions(request):
    query = request.GET.get('q', '')
    if len(query) < 3:
        return JsonResponse([], safe=False)
    suggestions = Movie.objects.filter(title__icontains=query).values(
        'title', 'genre', 'release_date', 'rating', 'random_slug', 'original_language'
    )
    return JsonResponse(list(suggestions), safe=False)


def get_word_details(word):
    word = word.replace('.', '').replace(',', '').replace('!', '').replace('?', '').lower()
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    headers = {
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data:
            definitions = data[0].get('meanings', [])
            if definitions:
                first_meaning = definitions[0]
                definition = first_meaning['definitions'][0]['definition']
                example = first_meaning['definitions'][0].get('example', 'No example available.')
                return {
                    'word': word,
                    'definition': definition,
                    'example': example
                }
    return None

def define(request):
    word = request.GET.get('word', '')
    if not word:
        return JsonResponse({'error': 'Word not provided'}, status=400)

    word_details = get_word_details(word)
    if word_details:
        return JsonResponse(word_details)
    return JsonResponse({'error': 'Word not found'}, status=404)

def upload_movie(request, slug_or_id):
    if request.method == 'POST':
        slug_or_id.replace('placeholder', '') if 'placeholder' in slug_or_id else slug_or_id
        #if the movie already exists and the video is existing, return error
        if Movie.objects.filter(random_slug=slug_or_id).exists():
            if Movie.objects.get(random_slug=slug_or_id).video:
                return JsonResponse({'error': 'Video already uploaded'}, status=400)
        video = request.FILES.get('video')
        transcript = request.FILES.get('transcript')
        if Movie.objects.filter(random_slug=slug_or_id).exists():
            pass
        else:
            if is_it_a_valid_imdb_id(slug_or_id):
                movie_data = get_movie_data_from_tmdb(slug_or_id)
                if 'error' not in movie_data:
                    Movie.objects.create(**movie_data)
        if not video:
            return JsonResponse({'error': 'No video provided'}, status=400)
        # Upload the video to S3
        video_key = upload_to_s3(video, f'uploads/{slug_or_id}/video/')
        # Upload the transcript to S3
        transcript = upload_to_s3(transcript, f'uploads/{slug_or_id}/transcript/')
        # Notify admin about the new upload
        notify_admin(
            movie=Movie.objects.get(random_slug=slug_or_id).title,
            title = 'New video available',
            message = 'A new video is available for you to watch',
            upload = f'https://filmfluency.fra1.cdn.digitaloceanspaces.com/uploads/{slug_or_id}',
            by = request.user
            
        )
        return JsonResponse({'success': True, 'message': 'Video uploaded successfully'})
    if request.method == 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    

def api_is_it_a_valid_imdb_id(request):
    imdb_id = request.GET.get('imdb_id', '')
    # return (data['movie_results'][0]['original_title'],data['movie_results'][0]['original_language'],data['movie_results'][0]['backdrop_path'])
    data = is_it_a_valid_imdb_id(imdb_id)
    if data:
        poster = f"https://image.tmdb.org/t/p/original{data[2]}" 
        return JsonResponse({'valid': True, 'title': data[0], 'language': data[1], 'poster': poster})
    return JsonResponse({'valid': False})


def notify_admin(movie, title, message, upload, by):
    send_email(title, f'{message}\n\nMovie: {movie}\nUploaded by: {by}\n\n{upload}')
    return JsonResponse({'success': True, 'message': 'Notification sent successfully'})

from contact.contact_logic import send_contact_email
def send_email(subject, message):
    send_contact_email(subject, message,recipient_list=settings.EMAIL_HOST_USER)