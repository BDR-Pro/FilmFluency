from django.urls import path
from .views import  crypto_payment, tap_payment , payment_home, products,how_its_works
app_name = 'payment'


urlpatterns = [

    path('tap-payment/', tap_payment, name='tap-payment'),
    path('subscribe/', payment_home, name='subscribe'),
    path('products/', products, name='products'),
    path('crypto-payment/', crypto_payment, name='crypto-payment'),
    path('how-it-works/', how_its_works, name='how-its-works'),
    
]