from django.urls import path
from .views import send_contact_request, send_message, send_whatsapp_message

app_name = 'contact'

urlpatterns = [
    path('send-contact-request/<str:email_type>/', send_contact_request, name='send-contact-request'),
    path('send-message/<str:contact_type>/', send_message, name='send-message'),
    path('send-whatsapp-message/', send_whatsapp_message, name='send-whatsapp-message'),
]
