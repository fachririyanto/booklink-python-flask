import re


# Email validation
# @source   https://www.geeksforgeeks.org/check-if-email-address-valid-or-not-in-python/
def is_email(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'

    return True if re.fullmatch(regex, email) else False
