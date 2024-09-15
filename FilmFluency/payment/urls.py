from django.urls import path
from .views import   payment_home, products,how_its_works,create_token
app_name = 'payment'


urlpatterns = [

    path('subscribe/', payment_home, name='subscribe'),
    path('products/', products, name='products'),
    path('create-token/', create_token, name='create-token'),
    path('how-it-works/', how_its_works, name='how-its-works'),
    
]