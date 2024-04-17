from django.http import JsonResponse
from upload_to_s3 import serve_secure_media
from decorators import check_paid_user

@check_paid_user
def secure_media_view(request, file_key):
    url = serve_secure_media(file_key)
    return JsonResponse({'url': url})