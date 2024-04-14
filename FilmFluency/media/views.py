from django.http import HttpResponse, Http404
from .models import OneTimeLink
import os

def serve_protected_media(request, content_type, token):
    try:
        link = OneTimeLink.objects.get(key=token, content_type=content_type, accessed=False)
        link.accessed = True
        link.save()

        # Serve the correct file based on content_type
        content_types = {
            'video': 'video/mp4',
            'audio': 'audio/wav',
            'transcript': 'text/plain'
        }
        with open(link.file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type=content_types[content_type])
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(link.file_path)
            return response
    except OneTimeLink.DoesNotExist:
        raise Http404("Link does not exist or has already been used")
