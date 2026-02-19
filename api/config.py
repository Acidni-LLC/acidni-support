"""
Configuration management for acidni-support.

Loads settings from environment variables and Azure Key Vault.
"""

import logging
from functools import lru_cache

from pydantic_settings import BaseSettings

logger = logging.getLogger("acidni-support.config")


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Environment
    environment: str = "dev"
    app_version: str = "1.0.0"
    log_level: str = "INFO"

    # Azure DevOps
    devops_org_url: str = "https://dev.azure.com/acidni"
    devops_pat: str = ""  # Loaded from Key Vault at startup

    # Cosmos DB
    cosmos_endpoint: str = "https://acidni-cosmos-dev.documents.azure.com:443/"
    cosmos_database: str = "support-dev"

    # Key Vault
    keyvault_url: str = "https://kv-terprint-dev.vault.azure.net"

    # APIM
    apim_base_url: str = "https://apim-terprint-dev.azure-api.net"

    # Notifications
    notifications_enabled: bool = True
    notification_email: str = "jamieson@acidni.net"

    # Application Insights
    applicationinsights_connection_string: str = ""

    model_config = {
        "env_prefix": "",
        "env_file": ".env",
        "case_sensitive": False,
    }


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
