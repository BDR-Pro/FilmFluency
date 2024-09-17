from django.conf import settings
from django.shortcuts import render, redirect
import requests
import logging
from .models import Product, Payment, code
from .functions import send_mail
logger = logging.getLogger(__name__)
from django.conf import settings
from django.contrib.auth.decorators import login_required
import random 
import base64
from django.http import JsonResponse
import json
import string
 

def products(request):
    #GET THE FIRST PRODUCT
    product = Product.objects.all()[0]

    return render(request, 'product.html', {'product': product})


    








def get_subject_and_message(product, nickname, quantity, isGift):
    if isGift:
        subject = f"Gift Subscription to {product} from FilmFluency"
        body = (
            f"Hi {nickname},\n\n"
            f"You will receive {quantity} activation code soon for a subscription to {product} from FilmFluency.\n\n"
            "Enjoy your gift!"
        )
    else:
        subject = f"Subscription to {product} from FilmFluency"
        body = (
            f"Hi {nickname},\n\n"
            f"You have successfully subscribed to {product} from FilmFluency.\n\n"
            "Enjoy!"
        )
    return subject, body


    
    

    

    


def how_its_works(request):
    return render(request, 'how_its_works.html')



def please_activate_your_email(request):
    return render(request, 'please_activate_your_email.html')

