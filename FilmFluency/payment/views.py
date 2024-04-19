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
from .functions import calc_weeks, get_currency_by_ip,exchange_rate_calc

logger = logging.getLogger(__name__)
from paypalrestsdk import Payment
from django.conf import settings
from django.http import JsonResponse
import paypalrestsdk
from django.contrib.auth.models import User

TAP_SECRET_KEY = settings.TAP_SECRET_KEY

"""
paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,  # 'sandbox' or 'live'
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET
})
"""
def create_product(request):
    iuser:User = request.user
    if not iuser.is_staff or not iuser.is_superuser:
        return HttpResponse("You are not authorized", status=401)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        
        price = request.POST.get('price')
        product = Product.objects.create(name=name, price=price)
        product.save()
        return HttpResponse(f"Product {name} created successfully with price {price}")
    else:
        return render(request, 'create_product.html')
    
def paypal_payment(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        product = Product.objects.get(name='Subscription')
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {"payment_method": "paypal"},
            "transactions": [{
                "amount": {
                    "total": str(product.price),
                    "currency": request.POST.get('currency', 'USD')
                },
                "description": f"Payment for {product.name} for {request.user.username}"
            }],
            "redirect_urls": {
                "return_url": request.build_absolute_uri('/payments/success/'),
                "cancel_url": request.build_absolute_uri('/payments/cancelled/')
            }
        })

        if payment.create():
            logger.info("Payment [%s] created successfully", payment.id)
            return JsonResponse({'approval_url': payment['links'][1]['href']})
        else:
            logger.error("Failed to create payment: %s", payment.error)
            return JsonResponse({'error': 'Failed to initiate PayPal payment'}, status=500)
    except Exception as e:
        logger.exception("An unexpected error occurred during PayPal payment creation")
        return JsonResponse({'error': str(e)}, status=500)

# Redirects based on payment choice
def payment_home(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        payment_method = request.POST.get('payment_method')

        if payment_method == 'crypto':
            return redirect('crypto_payment', amount=amount)
        
        elif payment_method == 'moysar':
            return redirect('initiate_payment')
        
        elif payment_method == 'paypal':
            return redirect('paypal_payment')
    else:
        return render(request, 'payment_home.html')


    

def crypto_payment(request):
    # Configuration for the CoinGate API
    api_url = "https://api.coingate.com/v2/orders"
    api_key = settings.COINGATE_API_KEY
    coin=request.get('coin', 'BTC')
    product = request.get('product', 'Subscription')
    price = Product.objects.get(name=product).price
    type_of_subscription = request.get('subscription', 'monthly')
    payment = Payment.objects.create(user=request.user, payment_method='crypto', is_completed=False, invoice=Invoice(amount=price, currency='USD'))
    payment.save()
    try:
        amount = float(price)
        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")
    except ValueError as e:
        logger.error(f"Invalid payment amount: {amount}. Error: {str(e)}")
        return HttpResponse(f"Invalid payment amount: {amount}", status=400)

    # Prepare the payload with the necessary details
    payload = {
        "order_id": str(payment.invoice_uuid),
        "price_amount": amount,
        "price_currency": "USD",
        "receive_currency": coin,
        "callback_url": request.build_absolute_uri('/payments/callback/'),  # URL to receive callbacks
        "cancel_url": request.build_absolute_uri('/payment/cancelled/'),  # URL for payment cancellation
        "success_url": request.build_absolute_uri('/payment/success/'),  # URL for successful payment
        "title": f"Payment for Subscription of FilmFluency {type_of_subscription}",
        "description": "Providing a entertaining and educational experience for learning languages.",
    }

    # Headers for the request
    headers = {
        'Authorization': f'Token {api_key}',
        'Content-Type': 'application/json'
    }

    # Making a POST request to the CoinGate API
    response = requests.post(api_url, json=payload, headers=headers)
    if response.status_code == 200:
        data = response.json()
        # Redirect the user to CoinGate payment page
        return HttpResponseRedirect(data['payment_url'])
    else:
        error_message = response.json().get('error', 'Failed to initiate crypto payment')
        logger.error(f"Crypto payment initiation failed: {error_message}")
        return HttpResponse(f"Failed to initiate crypto payment: {error_message}", status=400)
    
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
    return render(request, 'success.html')


def callback(request):
    # CoinGate payment callback logic
    pass


def product(request):

    product = Product.objects.all()
    ip = request.META.get('REMOTE_ADDR')
    preferred_currency = get_currency_by_ip(ip)
    
    for i in product:
        i.price = i.price * exchange_rate_calc(preferred_currency)
    return render(request, 'product.html', {'products': product, 'preferred_currency': preferred_currency})
    
    
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