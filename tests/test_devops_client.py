"""Tests for the Azure DevOps client."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from api.services.devops_client import DevOpsClient


class TestDevOpsClient:
    """Tests for DevOps work item creation."""

    def _make_client(self) -> DevOpsClient:
        """Create a DevOpsClient with test credentials."""
        return DevOpsClient(
            org_url="https://dev.azure.com/acidni",
            pat="test-pat-value",
        )

    @pytest.mark.asyncio
    async def test_create_work_item_bug(self):
        """Creating a Bug work item sends correct JSON Patch."""
        client = self._make_client()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": 42,
            "rev": 1,
            "url": "https://dev.azure.com/acidni/Terprint/_apis/wit/workItems/42",
            "fields": {
                "System.WorkItemType": "Bug",
                "System.TeamProject": "Terprint",
            },
        }
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as MockAsyncClient:
            mock_http = AsyncMock()
            mock_http.post.return_value = mock_response
            mock_http.__aenter__ = AsyncMock(return_value=mock_http)
            mock_http.__aexit__ = AsyncMock(return_value=None)
            MockAsyncClient.return_value = mock_http

            result = await client.create_work_item(
                project="Terprint",
                work_item_type="Bug",
                title="Widget not rendering",
                description="<p>The support widget fails to render.</p>",
                priority=1,
                area_path="Terprint\\Support",
                tags="acidni-support,bug,terprint-web",
            )

        assert result["id"] == 42
        assert result["type"] == "Bug"
        assert result["project"] == "Terprint"

        # Verify the POST was called with correct URL pattern
        call_args = mock_http.post.call_args
        url = call_args[0][0]
        assert "Terprint" in url
        assert "$Bug" in url
        assert "api-version=7.1" in url

    @pytest.mark.asyncio
    async def test_create_work_item_task(self):
        """Creating a Task work item for feature requests."""
        client = self._make_client()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": 100,
            "rev": 1,
            "url": "https://dev.azure.com/acidni/GridSight/_apis/wit/workItems/100",
            "fields": {
                "System.WorkItemType": "Task",
                "System.TeamProject": "GridSight",
            },
        }
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as MockAsyncClient:
            mock_http = AsyncMock()
            mock_http.post.return_value = mock_response
            mock_http.__aenter__ = AsyncMock(return_value=mock_http)
            mock_http.__aexit__ = AsyncMock(return_value=None)
            MockAsyncClient.return_value = mock_http

            result = await client.create_work_item(
                project="GridSight",
                work_item_type="Task",
                title="Add dark mode support",
                description="<p>Feature request: dark mode.</p>",
                priority=3,
                area_path="GridSight\\Support",
                tags="acidni-support,feature,gridsight",
            )

        assert result["id"] == 100
        assert result["type"] == "Task"
        assert result["project"] == "GridSight"

    @pytest.mark.asyncio
    async def test_build_work_item_url(self):
        """Work item URL is correctly formatted."""
        client = self._make_client()
        url = client._build_work_item_url("Terprint", 42)
        assert url == "https://dev.azure.com/acidni/Terprint/_workitems/edit/42"
