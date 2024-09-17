from django.urls import path
from .views import products,how_its_works
app_name = 'payment'


urlpatterns = [

    path('products/', products, name='products'),
    path('how-it-works/', how_its_works, name='how-its-works'),
    
]