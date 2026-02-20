"""
Licensing service — fetches subscription and support plan info from the Marketplace API.

Calls the acidni-publisher-portal subscription-lookup endpoint to retrieve
active subscriptions, plan details, and support tier information for a given user.
"""

import logging
from typing import Any

import httpx

from api.config import get_settings

logger = logging.getLogger("acidni-support.services.licensing")

# Map plan IDs to human-readable names (from publisher portal GetPlanDisplayName)
PLAN_DISPLAY_NAMES: dict[str, str] = {
    "free-trial-v1-0": "Free Trial",
    "free-trial-checkbox-v1-0": "Free Trial (30 Days)",
    "basic-v1-0": "Basic",
    "standard-v1-0": "Standard",
    "pro-v1-0": "Professional",
    "premium-v1-0": "Premium",
    "enterprise-v1-0": "Enterprise",
    "personal-v1-0": "Personal",
    "installer-v1-0": "Installer Pro",
    "solo-v1-0": "Solo",
    "solo-monthly-v1-0": "Solo (Monthly)",
    "team-v1-0": "Team",
    "business-v1-0": "Business",
    "internal-test-v1-0": "Internal Test",
}

# Plans that include priority support
PRIORITY_SUPPORT_PLANS = {"pro-v1-0", "premium-v1-0", "enterprise-v1-0"}

# Support plan offer IDs (standalone support subscriptions)
SUPPORT_OFFER_IDS = {
    "terprint-support-standard",
    "terprint-support-premium",
    "terprint-managed-services",
}

SUPPORT_PLAN_NAMES: dict[str, str] = {
    "terprint-support-standard": "Standard Support",
    "terprint-support-premium": "Premium Support",
    "terprint-managed-services": "Managed Services",
}


class LicensingService:
    """Fetch license and support plan info from the Marketplace API."""

    def __init__(self) -> None:
        settings = get_settings()
        self._base_url = f"{settings.apim_base_url}/marketplace/api"
        self._apim_key = settings.apim_subscription_key

    async def get_license_info(self, email: str) -> dict[str, Any]:
        """Look up subscriptions for a user by email.

        Returns a structured dict with:
            has_license: bool
            plan_name: str | None
            plan_id: str | None
            status: str | None
            is_free_trial: bool
            free_trial_end: str | None
            has_priority_support: bool
            support_plan: str | None
            subscriptions: list of subscription summaries
        """
        result: dict[str, Any] = {
            "has_license": False,
            "plan_name": None,
            "plan_id": None,
            "status": None,
            "is_free_trial": False,
            "free_trial_end": None,
            "has_priority_support": False,
            "support_plan": None,
            "subscriptions": [],
        }

        if not email:
            return result

        try:
            headers: dict[str, str] = {}
            if self._apim_key:
                headers["Ocp-Apim-Subscription-Key"] = self._apim_key

            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    f"{self._base_url}/subscription-lookup",
                    params={"email": email},
                    headers=headers,
                )

            if resp.status_code != 200:
                logger.warning(
                    "Subscription lookup failed for %s: HTTP %s",
                    email,
                    resp.status_code,
                )
                return result

            data = resp.json()
        except Exception:
            logger.exception("Failed to fetch license info for %s", email)
            return result

        # Parse the SubscriptionLookupResponse
        has_active = data.get("hasActiveSubscription", False)
        subscriptions = data.get("subscriptions", [])

        result["has_license"] = has_active

        # Separate product subscriptions from support subscriptions
        product_subs = []
        support_subs = []

        for sub in subscriptions:
            offer_id = sub.get("offerId", "")
            status = sub.get("status", "")

            summary = {
                "offer_id": offer_id,
                "plan_id": sub.get("planId"),
                "plan_name": sub.get("planDisplayName")
                or PLAN_DISPLAY_NAMES.get(sub.get("planId", ""), sub.get("planId")),
                "status": status,
                "is_free_trial": sub.get("isFreeTrial", False),
                "free_trial_end": sub.get("freeTrialEndDate"),
                "subscription_start": sub.get("subscriptionStartDate"),
                "subscription_end": sub.get("subscriptionEndDate"),
            }

            if offer_id in SUPPORT_OFFER_IDS:
                support_subs.append(summary)
            else:
                product_subs.append(summary)

        result["subscriptions"] = product_subs + support_subs

        # Pick the primary active product subscription
        active_product = next(
            (s for s in product_subs if s["status"] in ("Subscribed", "PendingActivation")),
            None,
        )
        if active_product:
            result["plan_id"] = active_product["plan_id"]
            result["plan_name"] = active_product["plan_name"]
            result["status"] = active_product["status"]
            result["is_free_trial"] = active_product["is_free_trial"]
            result["free_trial_end"] = active_product["free_trial_end"]

            # Check if plan includes priority support
            if active_product["plan_id"] in PRIORITY_SUPPORT_PLANS:
                result["has_priority_support"] = True

        # Check for standalone support subscription
        active_support = next(
            (s for s in support_subs if s["status"] in ("Subscribed", "PendingActivation")),
            None,
        )
        if active_support:
            result["support_plan"] = SUPPORT_PLAN_NAMES.get(
                active_support["offer_id"], active_support["plan_name"]
            )
            result["has_priority_support"] = True

        return result
