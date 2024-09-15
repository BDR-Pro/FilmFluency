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
   
def create_token(request):
    if request.method == 'GET':
        base64_params = request.GET.get('params')
        if base64_params:
            try:
                # Decode the Base64 string
                decoded_params = base64.b64decode(base64_params).decode('utf-8')
                # Parse the JSON string
                params = json.loads(decoded_params)

                quantity = params.get('quantity')
                subscriptionType = params.get('subscriptionType')
                isGift = params.get('isGift')
                paymentType = params.get('paymentType')
                print(f"Quantity: {quantity}, Subscription Type: {subscriptionType}, isGift: {isGift}, Payment Type: {paymentType} ")
            except Exception as e:
                print(f"Failed to parse parameters: {e}")

        try:
            id_= int(str(subscriptionType).replace(" ", ""))
            product = Product.objects.get(id=id_)
            payment = Payment.objects.create(
                user=request.user,
                product=product,
                is_completed=False,
                payment_method=paymentType,
                quantity=quantity,
                isGift=isGift,
                expires_at=timezone.now() + timezone.timedelta(weeks=calc_weeks(product))
            )
            
            if paymentType == 'crypto':
                print("Redirecting to crypto payment")
                return redirect('payment:crypto-payment', product=product.id)

        except:
            return JsonResponse({'error': 'Invalid payment method'})
    else:
        return render(request, 'payment.html')

def products(request):
    products = Product.objects.all()
    return render(request, 'product.html', {'products': products})

# Redirects based on payment choice
@login_required(login_url='users:login')
def payment_home(request):
    if request.method == 'GET':
        product = request.GET.get('product')
        product = Product.objects.get(id=product)
        subscription = Product.objects.all()
        return redirect(product.zid_url)

    







def genrate_gift_code(quantity, email,prouduct):
    
    for _ in range(quantity):
        ac_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=14))
        code.objects.create(code=ac_code)
        days=Product.objects.get(name=prouduct).days
        send_mail("Gift Subscription Code for filmfluency", f"Your gift subscription code is {ac_code} \n Number of days after activation {days}", email)

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

def product(request):

    product = Product.objects.all()
    
    for i in product:
        i.price = i.price * 3.75
    return render(request, 'product.html', {'products': product})
    
    
# Redirects based on payment choice
def cart(request):
    if request.method == 'POST':
        product = request.POST.get('product')
        currency = request.POST.get('currency')
        quantity = request.POST.get('quantity')
        
        for i in range(int(quantity)):
            Payment.objects.create(user=request.user, product=product, currency=currency, is_completed=False)
            
        
        for i in product:
            i.price = i.price * 3.75
            
        return render(request, 'payment.html', {'products': product, 'currency': currency, 'quantity': quantity})
    
    else:
        return render(request, 'payment.html')
    

    


def how_its_works(request):
    return render(request, 'how_its_works.html')



def please_activate_your_email(request):
    return render(request, 'please_activate_your_email.html')

