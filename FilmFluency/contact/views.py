# Create your views here.
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.http import HttpResponse
# Create your views here.
from django.http import JsonResponse
# Assume these utility functions are defined in a module named `email_utils.py`
from contact.contact_logic import send_contact_email, send_whatsapp_message , getMessage , getSubject
from django.shortcuts import redirect
from django.urls import reverse
from django.http import HttpResponse

"""contact type can be one of level_complete membership signup"""
def send_message(request, contact_type):
    if request.method == 'POST':
        # Extracting name, phone, and message from POST request
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        message = request.POST.get('message')

        # Sending WhatsApp message
        send_whatsapp_message(phone, message)
        
        return JsonResponse({'status': 'success'})
    else:
        return HttpResponse("Invalid request", status=400)

def send_contact_request(request, email_type):
    if request.method == 'POST':
        # Extracting name and email from POST request
        name = request.POST.get('name')
        email = request.POST.get('email')

        # Generating email subject and message
        subject = getSubject(email_type)
        message = getMessage(name, email, email_type)

        # Sending the email
        send_contact_email(subject, message, [email])
        if email_type == 'signup':
            return redirect(reverse('web:home'))

        else:
            return JsonResponse({'status': 'success'})
        # Redirect to a confirmation or success page
    else:
        return HttpResponse("Invalid request", status=400)

