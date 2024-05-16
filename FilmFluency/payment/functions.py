from .models import Product


def calc_weeks(product_name: str) -> float:
    """
    Calculate the number of weeks coverage based on the amount paid.

    Args:
    product_name (str): The name of the product to fetch its price and weeks.

    Returns:
    float: The number of weeks covered by the payment.
    """
    product = Product.objects.get(name=product_name)
    
    return product.days / 7


def send_mail(subject: str, message: str, recipient: str) -> None:
    """
    Send an email to the user.

    Args:
    subject (str): The subject of the email.
    message (str): The message to send.
    recipient (str): The email address of the recipient.

    Returns:
    None
    """
    pass