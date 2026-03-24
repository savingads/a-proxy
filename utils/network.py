"""
Network utilities for proxy configuration and IP info.

Replaces the Linux-only VPN utilities (utils/vpn.py) with
cross-platform proxy-based networking.
"""
import os
import logging
import requests

from config import PROXY_URL

logger = logging.getLogger(__name__)


def is_proxy_configured():
    """Check if a proxy URL is configured via environment."""
    return bool(PROXY_URL)


def get_proxy_url():
    """Get the currently configured proxy URL from environment."""
    return PROXY_URL


def get_ip_info(proxy_url=None):
    """
    Get current public IP information, optionally through a proxy.

    Args:
        proxy_url: Optional proxy URL to route the request through

    Returns:
        Dict with IP info from ipinfo.io, or dict with "error" key on failure
    """
    proxies = None
    if proxy_url:
        proxies = {"http": proxy_url, "https": proxy_url}

    retries = 3
    backoff_factor = 2
    for attempt in range(retries):
        try:
            response = requests.get("https://ipinfo.io", proxies=proxies, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Failed to get IP info: {e}")
            return {"error": "Failed to get IP info"}
        except requests.exceptions.RequestException as e:
            logger.error(f"Request exception: {e}")
            if hasattr(e, 'response') and e.response is not None and e.response.status_code == 429:
                import time
                wait_time = backoff_factor ** attempt
                logger.debug(f"Rate limited. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                return {"error": "Request exception"}
    return {"error": "Failed to get IP info after retries"}
