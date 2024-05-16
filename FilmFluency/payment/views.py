from django.conf import settings
from django.shortcuts import render, redirect
import requests
import logging
from .models import Product, Payment, Invoice, code
from django.utils import timezone
from .functions import calc_weeks,send_mail
from users.models import UserProfile
logger = logging.getLogger(__name__)
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from users.models import UserProfile
import random 
import string

TAP_SECRET_KEY = settings.TAP_SECRET_KEY

def get_icon_url(name):
    """Get the icon URL for a cryptocurrency."""
    list_of_cryptos = {
        'btc': 'https://upload.wikimedia.org/wikipedia/commons/4/46/Bitcoin.svg',
        'eth': 'https://upload.wikimedia.org/wikipedia/commons/0/05/Ethereum_logo_2014.svg',
        'xmr': 'https://cryptologos.cc/logos/monero-xmr-logo.png'
    }
    return list_of_cryptos.get(name.lower())

def get_crypto(amount):
    """Get QR code URL, name, icon URL, and amount converted for each cryptocurrency."""
    cryptos = turn_amount_to_crypto(amount)
    for crypto in cryptos:
        crypto['icon_url'] = get_icon_url(crypto['name'])
        # Assuming 'address' contains the necessary wallet address or it needs to be set before this function
        crypto['qr_code_url'] = get_qr_code_url(crypto['name'].lower())
        print(crypto)
    return cryptos
        
def turn_amount_to_crypto(amount):
    """Converts an amount in USD to equivalent amounts in major cryptocurrencies."""
    # Using Bitcoin, Ethereum, and Monero for this example
    amount = float(amount)
    api = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,monero&vs_currencies=usd"
    response = requests.get(api)
    if response.status_code == 200:
        data = response.json()
        return [
            {'name': 'BTC', 'amount': amount / float(data['bitcoin']['usd']), 'address': 'bc1qsgx0zpm802sw4ple68n0zpzp8ye84q3wyza0w8'},
            {'name': 'ETH', 'amount': amount / float(data['ethereum']['usd']), 'address': '0x7205d8e291DFb053422930146a4a488ce4c84eF2'},
            {'name': 'XMR', 'amount': amount / float(data['monero']['usd']), 'address': '47pGkqgeATm8u7Bzacz2xjNm6PgQUnaQm3WzWYPDKVjfHN2MXCojkpuUzxoNWvfmjcLVLGdqGf2Q2LmqxNesm9TcTfUrGf1'}
        ]
    else:
        print("Failed to fetch cryptocurrency data")
        return []

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
        return render(request, 'payment.html', {'product': product, 'subscriptions': subscription})
    if request.method == 'POST':
        product = request.POST.get('subscriptionType')
        currency = request.POST.get('isGift')
        quantity = request.POST.get('quantity')
        payment_type = request.POST.get('paymentType')
        
        new_payment = Payment.objects.create(user=request.user, product=product, currency=currency, is_completed=False, payment_method=payment_type, quantity=quantity)
        
        if payment_type == 'crypto':
            return redirect('payment:crypto-payment', payment_id=new_payment.id)
        if payment_type == 'tap':
            return redirect('payment:tap-payment', payment_id=new_payment.id)
        
    return render(request, 'payment.html')


    

def crypto_payment(request):
    amount="14"
    product = request.POST.get('product')
    amount = Product.objects.get(name=product).price

    crypto = get_crypto(amount)
    return render(request, 'crypto_payment.html', {'cryptos':crypto})

def create_token(request):
    
    quantity = request.POST.get('quantity')
    subscriptionType = request.POST.get('subscriptionType')
    isGift = request.POST.get('isGift')
    paymentType = request.POST.get('paymentType')
    product = Product.objects.get(id=subscriptionType)
    Payment.objects.create(user=request.user, product=product, is_completed=False,
                           payment_method=paymentType, quantity=quantity, isGift=isGift,
                            expires_at=timezone.now() + timezone.timedelta(weeks=calc_weeks(product)))
    if paymentType == 'crypto':
        redirect('payment:crypto-payment', product=product)
    if paymentType == 'tap':
        redirect('payment:tap-payment', product=product)
    
    else:
        return render(request, 'payment.html')

def tap_payment(request):
    if request.method == 'GET':
        return render(request, 'tap_payment.html')
    
    token = request.POST.get('token')
    product = request.POST.get('product')  
    amount = Product.objects.get(name=product).price
    order = Payment.objects.filter(user=request.user, is_completed=False).first()
    url = "https://api.tap.company/v2/charges"

    headers = {
        'Authorization': 'Bearer {TAP_SECRET_KEY}',
        'Content-Type': 'application/json'
    }
    profile = UserProfile.objects.get(user=request.user)
    first_name = profile.nickname
    email = request.user.email
    payload = {
        'amount': amount,
        'currency': 'SAR',
        'threeDSecure': True,
        'save_card': True,
        'description': f'FilmFluency Subscription of {product.name} for {first_name}',
        'statement_descriptor': 'FilmFluency',
        'metadata': {'udf1': 'subscribe', 'udf2': 'subscribe'},
        'reference': {'order': order.id},
        'receipt': {'email': True, 'sms': False},
        'customer': {
            'first_name': first_name,
            'email': email,
        },
        'source': {'id': token},
        'post': {'url': 'http://filmfluency.com/success', 'time': 10, 'method': 'POST'},
        'redirect': {'url': 'http://filmfluency.com', 'time': 10, 'method': 'GET'},
    }

    response = requests.post(url, json=payload, headers=headers)
    return JsonResponse(response.json())


def cancelled(request):
    Payment.objects.get(user=request.user, is_completed=False).delete()
    return render(request, 'cancelled.html')


def success(request):
    payment = Payment.objects.get(user=request.user, is_completed=False)
    payment.is_completed = True
    payment.save()
    
    """
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    """
    amount = Product.objects.get(name=payment.product).price*payment.quantity
    invoice = Invoice.objects.create(payment=payment, quantity=payment.quantity, amount=amount)
    invoice.subscreibed_at = timezone.now()
    invoice.expires_at = timezone.now() + timezone.timedelta(weeks=calc_weeks(payment.product))   
    invoice.save()
    profile = UserProfile.objects.get(user=request.user)
    profile.paid_user = True
    #catch the request json and get the card id and save it to the user profile
    profile.card_id = request.POST.get('card_id')
    profile.save()
    sub,body=get_subject_and_message(payment.product, profile.nickname,payment.quantity,payment.isGift)
    send_mail(sub, body, request.user.email)
    
    if payment.isGift:
        genrate_gift_code(payment.quantity, request.user.email, payment.product)
        
    return render(request, 'success.html')


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
    
    
    
    
def get_qr_code_url(crypto):
    """Get the QR code URL for a cryptocurrency."""
    return f"https://filmfluency.fra1.cdn.digitaloceanspaces.com/qr/{crypto}.png"

def how_its_works(request):
    return render(request, 'how_its_works.html')