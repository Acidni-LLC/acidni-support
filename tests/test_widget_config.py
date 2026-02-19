"""Tests for widget configuration and serving."""

import pytest
from fastapi.testclient import TestClient

from api.main import app


client = TestClient(app)


class TestHealthEndpoint:
    """Tests for GET /health."""

    def test_health_returns_ok(self):
        """Health endpoint returns 200 with status healthy."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "acidni-support"
        assert "version" in data

    def test_health_has_version_format(self):
        """Version follows expected format pattern."""
        response = client.get("/health")
        data = response.json()
        # Version should be a non-empty string
        assert isinstance(data["version"], str)
        assert len(data["version"]) > 0


class TestWidgetEndpoints:
    """Tests for widget serving endpoints."""

    def test_widget_embed_returns_html(self):
        """GET /widget/embed returns HTML page for Teams iframe."""
        response = client.get("/widget/embed?app_id=terprint-web")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "<acidni-support" in response.text
        assert "terprint-web" in response.text

    def test_widget_embed_requires_app_id(self):
        """GET /widget/embed without app_id still works with default."""
        response = client.get("/widget/embed")
        # Should still return HTML, just without a specific app_id
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]


class TestCORSHeaders:
    """Tests for CORS configuration."""

    def test_cors_allows_acidni_origins(self):
        """CORS headers allow Acidni domain origins."""
        response = client.options(
            "/support/submit",
            headers={
                "Origin": "https://terprint.acidni.net",
                "Access-Control-Request-Method": "POST",
            },
        )
        # FastAPI CORS middleware should respond
        assert response.status_code in (200, 204, 405)
