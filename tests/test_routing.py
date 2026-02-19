"""Tests for the routing service."""

import pytest
from pathlib import Path
from unittest.mock import patch

from api.services.routing_service import RoutingService


class TestRoutingService:
    """Tests for RoutingService YAML-based app routing."""

    def _get_test_config_path(self) -> str:
        """Return path to the real support-routing.yaml config."""
        return str(
            Path(__file__).parent.parent / "api" / "config" / "support-routing.yaml"
        )

    def test_resolve_known_app(self):
        """Known app_id resolves to correct DevOps project."""
        svc = RoutingService(self._get_test_config_path())
        result = svc.resolve("terprint-web")

        assert result["devops_project"] == "Terprint"
        assert result["area_path"] == "Terprint\\Support"
        assert result["app_name"] == "Terprint Web"

    def test_resolve_ai_service(self):
        """AI service app_id maps to Terprint project with correct area path."""
        svc = RoutingService(self._get_test_config_path())
        result = svc.resolve("terprint-ai-chat")

        assert result["devops_project"] == "Terprint"
        assert "AI Services" in result["area_path"]

    def test_resolve_cdes(self):
        """CDES app resolves to CDES DevOps project."""
        svc = RoutingService(self._get_test_config_path())
        result = svc.resolve("cdes")

        assert result["devops_project"] == "CDES"

    def test_resolve_unknown_app_falls_back_to_default(self):
        """Unknown app_id falls back to _default entry."""
        svc = RoutingService(self._get_test_config_path())
        result = svc.resolve("completely-unknown-app")

        assert result["devops_project"] == "Infrastructure"
        assert "Infrastructure" in result["area_path"]

    def test_resolve_gridsight(self):
        """GridSight routes to GridSight project."""
        svc = RoutingService(self._get_test_config_path())
        result = svc.resolve("gridsight")

        assert result["devops_project"] == "GridSight"

    def test_resolve_solar(self):
        """Solar app routes to SolarReporting project."""
        svc = RoutingService(self._get_test_config_path())
        result = svc.resolve("solar")

        assert result["devops_project"] == "SolarReporting"

    def test_resolve_all_configured_apps(self):
        """Every configured app_id should resolve without error."""
        svc = RoutingService(self._get_test_config_path())
        expected_apps = [
            "terprint-web",
            "terprint-ai-chat",
            "terprint-ai-recommender",
            "terprint-ai-deals",
            "terprint-ai-lab",
            "terprint-ai-health",
            "terprint-doctor-portal",
            "cdes",
            "acidni-sdo",
            "acidni-repolens",
            "fl-wetlands",
            "solar",
            "donate",
            "chat-analyzer",
            "text-a-truck",
            "veterans-build",
            "gridsight",
            "mobilemech",
            "minecraft",
            "devtools",
            "gowild-finder",
            "stepsafe",
            "infrastructure",
        ]
        for app_id in expected_apps:
            result = svc.resolve(app_id)
            assert "devops_project" in result, f"Missing devops_project for {app_id}"
            assert "area_path" in result, f"Missing area_path for {app_id}"
            assert "app_name" in result, f"Missing app_name for {app_id}"

    def test_reload(self):
        """Reload re-reads the YAML config without error."""
        svc = RoutingService(self._get_test_config_path())
        svc.reload()
        result = svc.resolve("terprint-web")
        assert result["devops_project"] == "Terprint"

    def test_all_routes_have_required_fields(self):
        """Every route in the config has devops_project, area_path, app_name."""
        svc = RoutingService(self._get_test_config_path())
        for app_id, route in svc._routes.items():
            assert "devops_project" in route, f"{app_id} missing devops_project"
            assert "area_path" in route, f"{app_id} missing area_path"
            assert "app_name" in route, f"{app_id} missing app_name"
