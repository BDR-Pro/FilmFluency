
from contact.contact_logic import send_contact_email



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
    send_contact_email(subject, message, recipient)
    