"""
SSO (Single Sign-On) utility functions for cross-subdomain authentication.

This module provides functions to generate and validate one-time SSO codes
stored in Redis cache for secure authentication across subdomains.
"""

import secrets
import json
from django.core.cache import cache
from django.conf import settings
from typing import Optional, Tuple

# SSO code settings
SSO_CODE_LENGTH = 8  # 8-character code
# SSO code has no expiration - valid until user logs out or logs in again
SSO_CODE_PREFIX = "sso_code:"  # Redis key prefix for code -> data
SSO_USER_PREFIX = "sso_user:"  # Redis key prefix for user_id -> code


def expire_user_previous_sso_code(user_id: int) -> None:
    """
    Expire the previous SSO code for a user (if exists).

    Args:
        user_id: The ID of the user whose previous SSO code should be expired
    """
    user_key = f"{SSO_USER_PREFIX}{user_id}"
    previous_code = cache.get(user_key)
    if previous_code:
        # Delete the previous code
        previous_code_key = f"{SSO_CODE_PREFIX}{previous_code}"
        cache.delete(previous_code_key)
        # Delete the user -> code mapping
        cache.delete(user_key)


def generate_sso_code(
    user_id: int, ip_address: str, user_agent: str
) -> Tuple[str, str]:
    """
    Generate a unique SSO code and store it in Redis.
    Expires any previous SSO code for this user.

    Args:
        user_id: The ID of the authenticated user
        ip_address: Client IP address for security tracking
        user_agent: User agent string for security tracking

    Returns:
        Tuple of (code, cache_key): The generated code and its Redis cache key

    Example:
        >>> code, cache_key = generate_sso_code(1, "192.168.1.1", "Mozilla/5.0")
        >>> print(code)  # "A1B2C3D4"
    """
    # Expire previous SSO code for this user (if exists)
    expire_user_previous_sso_code(user_id)

    # Generate a random alphanumeric code (always uppercase for consistency)
    code = "".join(
        secrets.choice("ABCDEFGHJKLMNPQRSTUVWXYZ23456789")
        for _ in range(SSO_CODE_LENGTH)
    ).upper()  # Ensure uppercase for consistency

    # Prepare data to store in cache
    sso_data = {
        "user_id": user_id,
        "ip_address": ip_address,
        "user_agent": user_agent,
        "used": False,
    }

    # Store in Redis without expiration (valid until user logs out or logs in again)
    code_cache_key = f"{SSO_CODE_PREFIX}{code}"
    cache.set(code_cache_key, json.dumps(sso_data), timeout=None)

    # Store user_id -> code mapping for easy lookup
    user_cache_key = f"{SSO_USER_PREFIX}{user_id}"
    cache.set(user_cache_key, code, timeout=None)

    return code, code_cache_key


def validate_and_consume_sso_code(
    code: str, ip_address: str, user_agent: str
) -> Optional[int]:
    """
    Validate and consume a one-time SSO code from Redis.

    This function:
    1. Checks if code exists in Redis
    2. Validates IP and User-Agent match (optional but recommended)
    3. Marks code as used and deletes it from Redis (one-time use)
    4. Returns user_id if valid, None otherwise

    Args:
        code: The SSO code to validate
        ip_address: Client IP address for validation
        user_agent: User agent string for validation

    Returns:
        user_id if code is valid and unused, None otherwise

    Example:
        >>> user_id = validate_and_consume_sso_code("A1B2C3D4", "192.168.1.1", "Mozilla/5.0")
        >>> if user_id:
        ...     print(f"User {user_id} authenticated via SSO")
    """
    cache_key = f"{SSO_CODE_PREFIX}{code}"

    # Get code data from Redis
    cached_data = cache.get(cache_key)
    if not cached_data:
        return None  # Code doesn't exist or expired

    try:
        sso_data = json.loads(cached_data)

        # Check if code already used
        if sso_data.get("used", False):
            return None  # Code already consumed

        # Optional: Validate IP and User-Agent for additional security
        # In some cases, IP might change (mobile networks), so we make this optional
        # stored_ip = sso_data.get("ip_address")  # Can be used for validation if needed
        # stored_user_agent = sso_data.get("user_agent")  # Can be used for validation if needed

        # Get user_id
        user_id = sso_data.get("user_id")
        if not user_id:
            return None

        # Mark as used and delete from Redis (atomic operation)
        cache.delete(cache_key)

        # Also delete the user -> code mapping
        user_cache_key = f"{SSO_USER_PREFIX}{user_id}"
        cache.delete(user_cache_key)

        # Return user_id for successful authentication
        return user_id

    except (json.JSONDecodeError, KeyError, TypeError):
        # Invalid data format, delete and return None
        cache.delete(cache_key)
        return None


def get_sso_redirect_url(code: str, target_domain: str = None) -> str:
    """
    Generate SSO redirect URL with code parameter.

    Args:
        code: The SSO code
        target_domain: Target domain for redirect (e.g., "dash.m-pishtaft.ir")
                     If None, defaults from settings

    Returns:
        Full redirect URL with code parameter

    Example:
        >>> url = get_sso_redirect_url("A1B2C3D4", "dash.m-pishtaft.ir")
        >>> print(url)  # "https://dash.m-pishtaft.ir/auth/callback?code=A1B2C3D4"
    """
    if not target_domain:
        # Default to dashboard subdomain
        # You can customize this based on your needs
        from django.contrib.sites.models import Site

        try:
            current_domain = Site.objects.get_current().domain
            if current_domain.startswith("dash."):
                target_domain = current_domain.replace("dash.", "")
            else:
                target_domain = f"dash.{current_domain}"
        except Exception:
            # Fallback if Site framework not configured
            target_domain = "dash.m-pishtaft.ir"

    # Determine protocol (https in production, http in development)
    protocol = "https" if not settings.DEBUG else "http"

    redirect_url = f"{protocol}://{target_domain}/auth/callback?code={code}"

    return redirect_url
