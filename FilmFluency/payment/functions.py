from .models import Product
import requests
from django.conf import settings

def calc_weeks(amount: float, product_name: str) -> float:
    """
    Calculate the number of weeks coverage based on the amount paid.

    Args:
    amount (float): The amount paid.
    product_name (str): The name of the product to fetch its price and weeks.

    Returns:
    float: The number of weeks covered by the payment.
    """
    product = Product.objects.get(name=product_name)
    
    quantity = max(amount / product.price, 1)  # Ensure a minimum of 1
    
    return product.weeks * quantity