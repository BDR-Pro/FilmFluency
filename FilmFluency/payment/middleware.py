# payment/middleware.py

from django.shortcuts import redirect
from django.urls import reverse
from payment.utils import is_user_active  

class PaymentAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the request is for the payment app
        if request.path.startswith('/payment/'):
            # Check if the user is active
            if not is_user_active(request.user):
                # Redirect to some other page or raise a permission denied error
                return redirect(reverse('payment:please_activate_your_email'))  # Change 'some_other_page' to your actual page

        response = self.get_response(request)
        return response
