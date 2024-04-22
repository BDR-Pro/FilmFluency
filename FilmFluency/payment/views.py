from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings
import requests
import logging
from .models import Product, Payment, Invoice
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .functions import calc_weeks
from users.models import UserProfile
logger = logging.getLogger(__name__)
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth.models import User

TAP_SECRET_KEY = settings.TAP_SECRET_KEY

def turn_amount_to_crypto(amount):
    """Converts an amount in USD to equivalent amounts in major cryptocurrencies."""
    # Including Bitcoin, Ethereum, Ripple, Monero, and Litecoin
    api = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,ripple,monero,litecoin&vs_currencies=usd"
    response = requests.get(api)
    data = response.json()
    btc = data['bitcoin']['usd']
    eth = data['ethereum']['usd']
    xmr = data['monero']['usd']
    
    # Calculating how much of each cryptocurrency you can buy with the given USD amount
    return {
        'BTC': amount / btc,
        'ETH': amount / eth,
        'XMR': amount / xmr,
    }

def products(request):
    products = Product.objects.all()
    return render(request, 'product.html', {'products': products})

# Redirects based on payment choice
def payment_home(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        payment_method = request.POST.get('payment_method')

        if payment_method == 'crypto':
            return redirect('crypto_payment', amount=amount)
        
        elif payment_method == 'tap':
            return redirect('tap_payment')
    else:
        return render(request, 'payment.html')


    

def crypto_payment(request):
    product = request.POST.get('product')
    amount = Product.objects.get(name=product).price
    amount = turn_amount_to_crypto(amount)
    return render(request, 'crypto_payment.html', {'amount': amount})

@require_http_methods(["POST"])
@csrf_exempt
def tap_payment(request):
    token = request.POST.get('token')
    product = request.POST.get('product')  
    amount = Product.objects.get(name=product).price
    
    url = "https://api.tap.company/v2/charges"
    
    headers = {
        'Authorization': 'Bearer {TAP_SECRET_KEY}'.format(TAP_SECRET_KEY='sk_test_XKokBfNWv6FIYuTMg5sLPjhJ'),
        'Content-Type': 'application/json'
    }
    
    payload = {
        'amount': amount,
        'currency': 'KWD',
        'threeDSecure': True,
        'save_card': False,
        'description': 'Charge Description',
        'statement_descriptor': 'Sample',
        'metadata': {'udf1': 'test 1', 'udf2': 'test 2'},
        'reference': {'transaction': 'txn_0001', 'order': 'ord_0001'},
        'receipt': {'email': False, 'sms': True},
        'customer': {
            'first_name': 'FirstName',
            'middle_name': 'MiddleName',
            'last_name': 'LastName',
            'email': 'email@domain.com',
            'phone': {'country_code': '965', 'number': '50000000'}
        },
        'source': {'id': token},
        'post': {'url': 'http://your_website.com/post_url'},
        'redirect': {'url': 'http://your_website.com/redirect_url'}
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
    invoice = payment.invoice
    invoice.is_paid = True
    invoice.subscreibed_at = timezone.now()
    invoice.expires_at = timezone.now() + timezone.timedelta(weeks=calc_weeks(invoice.amount, payment.product.name))   
    invoice.save()
    profile = UserProfile.objects.get(user=request.user)
    profile.paid_user = True
    return render(request, 'success.html')



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
            i.price = i.price * exchange_rate_calc(currency)
            
        return render(request, 'payment.html', {'products': product, 'currency': currency, 'quantity': quantity})
    
    else:
        return render(request, 'payment.html')