import re

def regex_email(email):
    pattern = re.compile(
        r"^(?P<local>[A-Za-z0-9!#$%&'*+/=?^_`{|}~.-]+)@(?P<domain>[A-Za-z0-9-]+\.[A-Za-z]{2,})$"
    )
    return validate_email_domain(email) if pattern.match(email) is not None else False


def validate_email_domain(email):
    # List of trusted email domains
    trusted_domains = {
        "gmail.com",
        "outlook.com",
        "yahoo.com",
        "icloud.com",
        "aol.com",
        "hotmail.com",
        "protonmail.com",
        "zoho.com",
        "yandex.com",
        "mail.com",
        "gmx.com",
        "tutanota.com",
        "fastmail.com",
        "disroot.org",
        "runbox.com",
        # Add other trusted domains as needed
    }

    # List of known disposable email domains
    disposable_domains = {
        "mailinator.com",
        "tempmail.com",
        "10minutemail.com",
        "throwawaymail.com",
        "guerrillamail.com",
        "yopmail.com",
        "temp-mail.org",
        "discard.email",
        "temp-mail.ru",
        "maildrop.cc",
      
        # Add more domains as needed
    }

    # Extract the domain from the email
    domain = email.split('@')[-1].strip().lower()

    # Check against trusted and disposable domain lists
    if domain in trusted_domains:
        return True  # It's a trusted email provider
    elif domain in disposable_domains:
        return False  # It's a disposable email provider
    else:
        return  True  # Not in either list, could be considered for further checks
