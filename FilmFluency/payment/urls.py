from django.urls import path
from .views import create_product, paypal_payment, tap_payment
app_name = 'payment'


urlpatterns = [
    path('create-product/', create_product, name='create-product'),
    path('paypal-payment/', paypal_payment, name='paypal-payment'),
    path('tap-payment/', tap_payment, name='tap-payment'),
]