from django.urls import path
from .views import serve_protected_media

urlpatterns = [
    path('<str:content_type>/<uuid:token>/', serve_protected_media, name='serve_protected_media'),
]
