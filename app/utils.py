import random
import string
from urllib.parse import urlparse

def generate_short_code(length=6):
    """
    Generate a random alphanumeric short code of given length.
    """
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))

def is_valid_url(url):
    """
    Validate a URL. Returns True if the URL has http/https scheme and a netloc.
    """
    try:
        result = urlparse(url)
        return all([result.scheme in ("http", "https"), result.netloc])
    except Exception:
        return False