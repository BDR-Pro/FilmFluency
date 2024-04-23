from django.urls import path
from .views import secure_media_view,search_suggestions

app_name = 'api'

urlpatterns = [
    path('secure-media/<str:file_key>/', secure_media_view, name='secure_media_view'),
    path('search-suggestions/', search_suggestions, name='search_suggestions'),
]
