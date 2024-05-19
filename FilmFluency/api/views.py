from django.http import JsonResponse
from api.upload_to_s3 import serve_secure_media
from api.decorators import check_paid_user
from learning.models import Movie

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