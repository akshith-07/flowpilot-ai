"""
Utility functions for FlowPilot AI.
"""
import hashlib
import secrets
import string
from typing import Optional
from django.utils.text import slugify as django_slugify


def generate_random_string(length: int = 32, include_punctuation: bool = False) -> str:
    """
    Generate a cryptographically secure random string.

    Args:
        length: Length of the string
        include_punctuation: Include punctuation characters

    Returns:
        Random string
    """
    alphabet = string.ascii_letters + string.digits
    if include_punctuation:
        alphabet += string.punctuation
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def generate_api_key() -> tuple[str, str]:
    """
    Generate an API key and its hash.

    Returns:
        Tuple of (api_key, api_key_hash)
    """
    prefix = 'fp_'
    key = generate_random_string(32)
    api_key = f'{prefix}{key}'
    api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    return api_key, api_key_hash


def hash_string(value: str) -> str:
    """
    Hash a string using SHA256.

    Args:
        value: String to hash

    Returns:
        Hex digest of hash
    """
    return hashlib.sha256(value.encode()).hexdigest()


def slugify(value: str, allow_unicode: bool = False) -> str:
    """
    Convert string to slug format.

    Args:
        value: String to slugify
        allow_unicode: Allow unicode characters

    Returns:
        Slugified string
    """
    return django_slugify(value, allow_unicode=allow_unicode)


def unique_slugify(instance, value: str, slug_field_name: str = 'slug', queryset=None) -> str:
    """
    Generate a unique slug for a model instance.

    Args:
        instance: Model instance
        value: Value to slugify
        slug_field_name: Name of the slug field
        queryset: Optional queryset to check uniqueness against

    Returns:
        Unique slug
    """
    slug = slugify(value)
    unique_slug = slug

    if queryset is None:
        queryset = instance.__class__.objects.all()

    if instance.pk:
        queryset = queryset.exclude(pk=instance.pk)

    counter = 1
    while queryset.filter(**{slug_field_name: unique_slug}).exists():
        unique_slug = f'{slug}-{counter}'
        counter += 1

    return unique_slug


def get_client_ip(request) -> Optional[str]:
    """
    Get client IP address from request.

    Args:
        request: HTTP request

    Returns:
        IP address or None
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_agent(request) -> str:
    """
    Get user agent from request.

    Args:
        request: HTTP request

    Returns:
        User agent string
    """
    return request.META.get('HTTP_USER_AGENT', '')


def bytes_to_mb(bytes_value: int) -> float:
    """
    Convert bytes to megabytes.

    Args:
        bytes_value: Value in bytes

    Returns:
        Value in megabytes
    """
    return round(bytes_value / (1024 * 1024), 2)


def bytes_to_gb(bytes_value: int) -> float:
    """
    Convert bytes to gigabytes.

    Args:
        bytes_value: Value in bytes

    Returns:
        Value in gigabytes
    """
    return round(bytes_value / (1024 * 1024 * 1024), 2)


def calculate_cost(tokens: int, model: str) -> float:
    """
    Calculate cost in USD for AI API usage.

    Args:
        tokens: Number of tokens
        model: Model name

    Returns:
        Cost in USD
    """
    # Pricing per 1M tokens (as of 2024)
    pricing = {
        'gemini-1.5-pro': {
            'input': 3.50,
            'output': 10.50,
        },
        'gemini-1.5-flash': {
            'input': 0.35,
            'output': 1.05,
        },
    }

    if model not in pricing:
        return 0.0

    # Assuming tokens are output tokens (conservative estimate)
    cost_per_token = pricing[model]['output'] / 1_000_000
    return round(tokens * cost_per_token, 6)
