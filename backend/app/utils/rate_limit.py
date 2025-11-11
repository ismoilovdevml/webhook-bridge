"""Rate limiting utilities with proxy support."""

from fastapi import Request


def get_client_ip(request: Request) -> str:
    """
    Get client IP address with proxy support.

    Checks X-Forwarded-For and X-Real-IP headers for proxied requests.
    Falls back to direct client IP if headers not present.

    Args:
        request: FastAPI request object

    Returns:
        Client IP address

    Security Note:
        Only trust X-Forwarded-For if you have a trusted proxy (nginx, cloudflare, etc.)
        in front of your application. Configure TRUSTED_PROXIES in settings if needed.
    """
    # Check X-Forwarded-For header (standard for proxies)
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        # X-Forwarded-For can contain multiple IPs: "client, proxy1, proxy2"
        # Take the first (leftmost) IP as the original client
        client_ip = forwarded_for.split(",")[0].strip()
        return client_ip

    # Check X-Real-IP header (nginx, cloudflare)
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()

    # Check CF-Connecting-IP (Cloudflare)
    cf_ip = request.headers.get("cf-connecting-ip")
    if cf_ip:
        return cf_ip.strip()

    # Fallback to direct client IP
    if request.client:
        return request.client.host

    # Last resort
    return "unknown"


def get_rate_limit_key(request: Request) -> str:
    """
    Generate rate limit key based on client IP.

    Can be extended to use API keys or user IDs for authenticated requests.

    Args:
        request: FastAPI request object

    Returns:
        Rate limit key string
    """
    client_ip = get_client_ip(request)

    # For authenticated requests, you could use API key or user ID
    # Example:
    # api_key = request.headers.get("x-api-key")
    # if api_key:
    #     return f"api_key:{api_key}"

    return f"ip:{client_ip}"
