"""
API key authentication for acidni-support.

Validates ``Ocp-Apim-Subscription-Key`` or ``X-Api-Key`` header on protected
API routes.  Health checks, widget static assets, the landing page, and the
widget embed page remain unauthenticated so browsers and container probes can
reach them directly.

The expected key is loaded from Azure Key Vault at startup (see main.py
lifespan).  In local development the key can be supplied via the
``SUPPORT_API_KEY`` environment variable.
"""

import hmac
import logging

from fastapi import Header, HTTPException

from api.config import get_settings

logger = logging.getLogger("acidni-support.auth")


async def require_api_key(
    ocp_apim_subscription_key: str | None = Header(None),
    x_api_key: str | None = Header(None),
) -> str:
    """FastAPI dependency that enforces API-key authentication.

    Accepts the key in either ``Ocp-Apim-Subscription-Key`` (APIM standard)
    or ``X-Api-Key`` (generic fallback).  Returns the validated key value.

    Raises 401 if neither header is present or the value does not match.
    """
    settings = get_settings()
    expected = settings.support_api_key

    if not expected:
        # Auth not configured — allow (log a warning so ops can notice)
        logger.warning("SUPPORT_API_KEY not configured — skipping auth check")
        return ""

    provided = ocp_apim_subscription_key or x_api_key
    if not provided:
        raise HTTPException(
            status_code=401,
            detail="Missing API key. Provide Ocp-Apim-Subscription-Key or X-Api-Key header.",
        )

    if not hmac.compare_digest(provided, expected):
        logger.warning("Invalid API key attempt")
        raise HTTPException(status_code=401, detail="Invalid API key.")

    return provided
