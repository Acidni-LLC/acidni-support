"""
Notification service — sends email confirmations via Azure Communication Services.
"""

import logging

import httpx

from api.config import get_settings

logger = logging.getLogger("acidni-support.services.notification")


class NotificationService:
    """Send notifications for support tickets via the Terprint Communications API."""

    def __init__(self) -> None:
        settings = get_settings()
        self._apim_url = settings.apim_base_url
        self._apim_key = settings.apim_subscription_key
        self._enabled = settings.notifications_enabled
        self._from_email = settings.notifications_from_email
        self._client = httpx.AsyncClient(timeout=15.0)

    async def send_confirmation(
        self,
        to_email: str,
        ticket_id: str,
        subject: str,
        app_name: str,
    ) -> bool:
        """Send a ticket confirmation email to the reporter."""
        if not self._enabled:
            logger.info("Notifications disabled – skipping confirmation for %s", ticket_id)
            return False

        if not to_email:
            return False

        body_html = f"""
        <div style="font-family: system-ui, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #2563eb;">Support Request Received</h2>
            <p>Thank you for contacting Acidni Support.</p>
            <table style="border-collapse: collapse; width: 100%; margin: 16px 0;">
                <tr>
                    <td style="padding: 8px; border-bottom: 1px solid #e5e7eb; font-weight: bold;">Ticket ID</td>
                    <td style="padding: 8px; border-bottom: 1px solid #e5e7eb;">{ticket_id}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border-bottom: 1px solid #e5e7eb; font-weight: bold;">Subject</td>
                    <td style="padding: 8px; border-bottom: 1px solid #e5e7eb;">{subject}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border-bottom: 1px solid #e5e7eb; font-weight: bold;">Application</td>
                    <td style="padding: 8px; border-bottom: 1px solid #e5e7eb;">{app_name}</td>
                </tr>
            </table>
            <p>We'll review your request and get back to you shortly.</p>
            <p style="color: #6b7280; font-size: 0.875rem;">— Acidni Support Team</p>
        </div>
        """

        try:
            response = await self._client.post(
                f"{self._apim_url}/communications/api/send-email",
                headers={
                    "Ocp-Apim-Subscription-Key": self._apim_key,
                    "Content-Type": "application/json",
                },
                json={
                    "to": to_email,
                    "subject": f"[Acidni Support] {subject} — {ticket_id}",
                    "body": body_html,
                    "from": self._from_email,
                },
            )
            if response.status_code in (200, 201, 202):
                logger.info("Confirmation email sent for %s to %s", ticket_id, to_email)
                return True
            logger.warning(
                "Email send returned %s for %s",
                response.status_code,
                ticket_id,
            )
            return False
        except Exception:
            logger.exception("Failed to send confirmation email for %s", ticket_id)
            return False

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()
