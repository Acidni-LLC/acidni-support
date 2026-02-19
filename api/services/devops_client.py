"""
Azure DevOps REST API client — creates work items for support tickets.
"""

import logging
from base64 import b64encode
from typing import Any

import httpx

logger = logging.getLogger("acidni-support.services.devops_client")


class DevOpsClient:
    """Azure DevOps REST API client for work item creation."""

    API_VERSION = "7.1"

    def __init__(self, org_url: str, pat: str) -> None:
        self._org_url = org_url.rstrip("/")
        self._auth_header = self._build_auth_header(pat)
        self._client = httpx.AsyncClient(timeout=30.0)

    @staticmethod
    def _build_auth_header(pat: str) -> str:
        """Build Basic auth header from PAT."""
        encoded = b64encode(f":{pat}".encode()).decode()
        return f"Basic {encoded}"

    async def create_work_item(
        self,
        project: str,
        work_item_type: str,
        title: str,
        description: str,
        area_path: str | None = None,
        priority: int = 3,
        tags: str = "",
    ) -> dict[str, Any]:
        """Create a work item in Azure DevOps.

        Returns dict with 'id', 'url', 'rev' keys.
        """
        url = (
            f"{self._org_url}/{project}/_apis/wit/workitems"
            f"/${work_item_type}?api-version={self.API_VERSION}"
        )

        # Build JSON Patch document
        operations: list[dict[str, Any]] = [
            {"op": "add", "path": "/fields/System.Title", "value": title},
            {"op": "add", "path": "/fields/System.Description", "value": description},
            {"op": "add", "path": "/fields/Microsoft.VSTS.Common.Priority", "value": priority},
        ]

        if area_path:
            operations.append(
                {"op": "add", "path": "/fields/System.AreaPath", "value": area_path}
            )

        if tags:
            operations.append(
                {"op": "add", "path": "/fields/System.Tags", "value": tags}
            )

        headers = {
            "Authorization": self._auth_header,
            "Content-Type": "application/json-patch+json",
        }

        response = await self._client.post(url, json=operations, headers=headers)

        if response.status_code not in (200, 201):
            logger.error(
                "DevOps API error: %s %s — %s",
                response.status_code,
                response.reason_phrase,
                response.text[:500],
            )
            raise RuntimeError(
                f"Azure DevOps API returned {response.status_code}: {response.text[:200]}"
            )

        data = response.json()
        work_item_id = data["id"]
        web_url = data.get("_links", {}).get("html", {}).get("href", "")

        logger.info(
            "Created %s #%s in %s — %s",
            work_item_type,
            work_item_id,
            project,
            title[:80],
        )

        return {
            "id": work_item_id,
            "url": web_url,
            "rev": data.get("rev", 1),
            "type": work_item_type,
            "project": project,
        }

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()
