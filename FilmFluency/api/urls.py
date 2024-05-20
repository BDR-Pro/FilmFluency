from django.urls import path
from .views import secure_media_view,search_suggestions,define,upload_movie,api_is_it_a_valid_imdb_id

from rest_framework_simplejwt.views import TokenObtainPairView

app_name = 'api'

urlpatterns = [
    path('secure-media/<str:file_key>/', secure_media_view, name='secure_media_view'),
    path('search-suggestions/', search_suggestions, name='search_suggestions'),
    path('define/', define, name='define'),
    path('upload-movie/<str:slug_or_id>', upload_movie, name='upload_movie'),
    path('is-it-a-valid-imdb-id/<str:imdb_id>', api_is_it_a_valid_imdb_id, name='api_is_it_a_valid_imdb_id'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
]
