"""Tests for support submission endpoint."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient

from api.main import app
from api.models import SupportCategory


client = TestClient(app)


class TestSubmitEndpoint:
    """Tests for POST /support/submit."""

    def _build_payload(self, **overrides) -> dict:
        """Build a valid submit payload with optional overrides."""
        payload = {
            "app_id": "terprint-web",
            "category": "bug",
            "subject": "Page not loading",
            "description": "The analytics page fails to load when I click on it.",
            "user_email": "user@example.com",
            "user_name": "Test User",
            "priority": 2,
        }
        payload.update(overrides)
        return payload

    @patch("api.routes.support._get_cosmos_service")
    @patch("api.routes.support._get_devops_client")
    @patch("api.routes.support._get_routing_service")
    @patch("api.routes.support._get_notification_service")
    def test_submit_success(
        self,
        mock_notif_svc,
        mock_routing_svc,
        mock_devops_client,
        mock_cosmos_svc,
    ):
        """Valid submission creates DevOps work item and Cosmos ticket."""
        # Arrange
        mock_routing = MagicMock()
        mock_routing.resolve.return_value = {
            "devops_project": "Terprint",
            "area_path": "Terprint\\Support",
            "app_name": "Terprint Web",
        }
        mock_routing_svc.return_value = mock_routing

        mock_devops = AsyncMock()
        mock_devops.create_work_item.return_value = {
            "id": 12345,
            "url": "https://dev.azure.com/acidni/Terprint/_workitems/edit/12345",
            "rev": 1,
            "type": "Bug",
            "project": "Terprint",
        }
        mock_devops_client.return_value = mock_devops

        mock_cosmos = AsyncMock()
        mock_cosmos.save_ticket.return_value = None
        mock_cosmos.save_audit_log.return_value = None
        mock_cosmos_svc.return_value = mock_cosmos

        mock_notif = AsyncMock()
        mock_notif.send_confirmation.return_value = None
        mock_notif_svc.return_value = mock_notif

        # Act
        response = client.post("/support/submit", json=self._build_payload())

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "created"
        assert data["devops_work_item_id"] == 12345
        assert data["ticket_id"].startswith("SUP-")
        assert "devops_work_item_url" in data

    def test_submit_missing_required_fields(self):
        """Missing required fields return 422."""
        response = client.post("/support/submit", json={"app_id": "terprint-web"})
        assert response.status_code == 422

    def test_submit_invalid_category(self):
        """Invalid category returns 422."""
        payload = self._build_payload(category="invalid_cat")
        response = client.post("/support/submit", json=payload)
        assert response.status_code == 422

    def test_submit_empty_subject(self):
        """Empty subject returns 422."""
        payload = self._build_payload(subject="")
        response = client.post("/support/submit", json=payload)
        assert response.status_code == 422

    def test_submit_empty_description(self):
        """Empty description returns 422."""
        payload = self._build_payload(description="")
        response = client.post("/support/submit", json=payload)
        assert response.status_code == 422

    @patch("api.routes.support._get_cosmos_service")
    @patch("api.routes.support._get_devops_client")
    @patch("api.routes.support._get_routing_service")
    @patch("api.routes.support._get_notification_service")
    def test_submit_with_context(
        self,
        mock_notif_svc,
        mock_routing_svc,
        mock_devops_client,
        mock_cosmos_svc,
    ):
        """Submission with context metadata passes through."""
        mock_routing = MagicMock()
        mock_routing.resolve.return_value = {
            "devops_project": "Terprint",
            "area_path": "Terprint\\Support",
            "app_name": "Terprint Web",
        }
        mock_routing_svc.return_value = mock_routing

        mock_devops = AsyncMock()
        mock_devops.create_work_item.return_value = {
            "id": 99,
            "url": "https://dev.azure.com/acidni/Terprint/_workitems/edit/99",
            "rev": 1,
            "type": "Task",
            "project": "Terprint",
        }
        mock_devops_client.return_value = mock_devops

        mock_cosmos = AsyncMock()
        mock_cosmos.save_ticket.return_value = None
        mock_cosmos.save_audit_log.return_value = None
        mock_cosmos_svc.return_value = mock_cosmos

        mock_notif = AsyncMock()
        mock_notif.send_confirmation.return_value = None
        mock_notif_svc.return_value = mock_notif

        payload = self._build_payload(
            category="feature",
            context={
                "url": "https://terprint.acidni.net/analytics",
                "browser": "Chrome 120",
                "os": "Windows 11",
                "app_version": "v20260201-1430",
                "screen_resolution": "1920x1080",
            },
        )
        response = client.post("/support/submit", json=payload)
        assert response.status_code == 200

    def test_submit_priority_bounds(self):
        """Priority must be 1-4."""
        payload = self._build_payload(priority=5)
        response = client.post("/support/submit", json=payload)
        assert response.status_code == 422

        payload = self._build_payload(priority=0)
        response = client.post("/support/submit", json=payload)
        assert response.status_code == 422


class TestConfigEndpoint:
    """Tests for GET /support/config/{app_id}."""

    @patch("api.routes.support._get_routing_service")
    def test_config_known_app(self, mock_routing_svc):
        """Known app_id returns widget configuration."""
        mock_routing = MagicMock()
        mock_routing.resolve.return_value = {
            "devops_project": "Terprint",
            "area_path": "Terprint\\Support",
            "app_name": "Terprint Web",
        }
        mock_routing_svc.return_value = mock_routing

        response = client.get("/support/config/terprint-web")
        assert response.status_code == 200
        data = response.json()
        assert data["app_id"] == "terprint-web"
        assert "categories" in data
        assert len(data["categories"]) == 4

    @patch("api.routes.support._get_routing_service")
    def test_config_unknown_app_uses_default(self, mock_routing_svc):
        """Unknown app_id falls back to _default routing."""
        mock_routing = MagicMock()
        mock_routing.resolve.return_value = {
            "devops_project": "Infrastructure",
            "area_path": "Infrastructure\\Support",
            "app_name": "Unknown App",
        }
        mock_routing_svc.return_value = mock_routing

        response = client.get("/support/config/unknown-app-xyz")
        assert response.status_code == 200
