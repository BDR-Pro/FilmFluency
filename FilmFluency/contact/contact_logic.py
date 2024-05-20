from django.core.mail import send_mail
from django.conf import settings
from twilio.rest import Client
from django.template.loader import render_to_string

def getbody(body_type):
    messages = {
        
        'signup': "Thank you for signing up! We're excited to have you join us.",
        'membership': "Your membership has been confirmed. Welcome to the club!",
        'level_complete': "Awesome job on completing level 10! Ready for more challenges?",
    }
    return messages.get(body_type, "Here's a special message just for you!")

def getMessage(name, email, email_type):
    context = {
        'name': name,
        'email': email,
    }
    # Based on the type, render a specific template
    if email_type == 'signup':
        return render_to_string('emails/signup.html', context)
    elif email_type == 'membership':
        return render_to_string('emails/membership.html', context)
    elif email_type == 'level_complete':
        context['level'] = 10  # Assuming level 10 completion, adjust as necessary
        return render_to_string('emails/level_complete.html', context)
    else:
        return render_to_string('emails/general_info.html', context)


def getSubject(email_type):
    subjects = {
        'signup': "Welcome to Our Community!",
        'membership': "Membership Confirmation",
        'level_complete': "Congratulations on Your New Level!",
        'general_info': "Important Information About Your Account"
    }
    return subjects.get(email_type, "Important Notification")

def send_contact_email(subject, message, recipient_list):
    
    email_from = settings.EMAIL_HOST_USER
    send_mail(subject, message, email_from, recipient_list)


def send_whatsapp_message(to, body):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    body=getbody(body)
    message = client.messages.create(
        body=body,
        from_=f'whatsapp:{settings.TWILIO_WHATSAPP_NUMBER}',
        to=f'whatsapp:{to}'
    )
    return message.sid
