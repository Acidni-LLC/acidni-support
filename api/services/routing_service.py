"""
Routing service — resolves app_id to Azure DevOps project + area path.

Loads routing configuration from support-routing.yaml and provides
fast lookups for mapping application submissions to the correct
DevOps project and area path.
"""

import logging
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger("acidni-support.services.routing")

_CONFIG_PATH = Path(__file__).parent.parent / "config" / "support-routing.yaml"


class RoutingService:
    """Map app_id values to Azure DevOps projects and area paths."""

    def __init__(self, config_path: Path | None = None) -> None:
        self._config_path = config_path or _CONFIG_PATH
        self._routes: dict[str, dict[str, Any]] = {}
        self._load()

    def _load(self) -> None:
        """Load routing configuration from YAML."""
        if not self._config_path.exists():
            logger.warning("Routing config not found at %s — using empty routing", self._config_path)
            return
        with open(self._config_path) as fh:
            data = yaml.safe_load(fh)
        if not data or "routes" not in data:
            logger.warning("Routing config has no 'routes' key")
            return
        for route in data["routes"]:
            app_id = route.get("app_id")
            if app_id:
                self._routes[app_id] = route
        logger.info("Loaded %d support routes", len(self._routes))

    def resolve(self, app_id: str) -> dict[str, Any] | None:
        """Resolve an app_id to its routing configuration.

        Returns dict with keys: devops_project, area_path, app_name, etc.
        Returns None if no route found.
        """
        return self._routes.get(app_id)

    def list_app_ids(self) -> list[str]:
        """Return all configured app IDs."""
        return [k for k in self._routes if not k.startswith("_")]

    def reload(self) -> None:
        """Hot-reload routing config."""
        self._routes.clear()
        self._load()
