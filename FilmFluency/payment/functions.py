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

def exchange_rate_calc(currency: str) -> float:
    """
    Calculate the exchange rate for a given currency.
    
    Args:
    currency (str): Currency code to get the exchange rate for.
    
    Returns:
    float: The exchange rate if known, otherwise defaults to 1.
    """
    exchange_price = {
        'AED': 3.67, 'SAR': 3.75, 'QAR': 3.64, 'OMR': 0.38,
        'KWD': 0.30, 'BHD': 0.38
    }
    return exchange_price.get(currency, 1)


def get_currency_by_ip(ip: str) -> str:
    """
    Get the currency based on the user's IP location using an IP geolocation API.

    Args:
    ip (str): IP address of the user.

    Returns:
    str: Currency code, defaults to 'USD' if not in a Gulf country or on error.
    """
    gulf = {
        'SA': 'SAR', 'AE': 'AED', 'QA': 'QAR',
        'OM': 'OMR', 'KW': 'KWD', 'BH': 'BHD'
    }

    try:
        url = f"https://ipinfo.io/{ip}/json?token={settings.IPINFO_API_KEY}"
        response = requests.get(url)
        response.raise_for_status()  # Will raise an HTTPError if the HTTP request returned an unsuccessful status code
        data = response.json()
        country = data.get('country')

        return gulf.get(country, 'USD')
    except requests.RequestException:
        return 'USD'

