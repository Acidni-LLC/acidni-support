"""
acidni-support — FastAPI application entry point.

Centralized support and feedback collection API for all Acidni products.
Receives support requests from the embeddable widget, resolves the app's
CMDB ID to an Azure DevOps project, and creates work items automatically.

acidni-support v1.0.0
"""

import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.config import get_settings

__version__ = "1.0.0"

# Configure logging to stdout so container logs capture application messages
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)

logger = logging.getLogger("acidni-support")

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load secrets from Key Vault at startup."""
    try:
        from azure.identity import DefaultAzureCredential
        from azure.keyvault.secrets import SecretClient

        credential = DefaultAzureCredential()
        kv_client = SecretClient(vault_url=settings.keyvault_url, credential=credential)
        pat = kv_client.get_secret("azure-devops-pat").value
        if pat:
            settings.devops_pat = pat
            logger.info("Loaded DevOps PAT from Key Vault")
        else:
            logger.warning("DevOps PAT not found in Key Vault")
    except Exception as e:
        logger.warning("Could not load secrets from Key Vault: %s", e)
    yield


app = FastAPI(
    title="Acidni Support API",
    description="Centralized support and feedback collection for all Acidni apps",
    version=__version__,
    docs_url="/docs" if settings.environment == "dev" else None,
    redoc_url=None,
    lifespan=lifespan,
)

# -------------------------------------------------------------------
# CORS — allow widget origins + Teams
# -------------------------------------------------------------------
ALLOWED_ORIGINS = [
    "https://sdo.acidni.net",
    "https://terprint.acidni.net",
    "https://solar.acidni.net",
    "https://gridsight.acidni.net",
    "https://flwm.acidni.net",
    "https://mobilemech.acidni.net",
    "https://donate.acidni.net",
    "https://textatruck.acidni.net",
    "https://minecraft.acidni.net",
    "https://www.cdes.world",
    "https://sales.terprint.com",
    "https://sales.solar.acidni.net",
    "https://sales.gridsight.acidni.net",
    "https://support.acidni.net",
    # Teams
    "https://teams.microsoft.com",
    "https://*.teams.microsoft.com",
    # Local development
    "http://localhost:3000",
    "http://localhost:5000",
    "http://localhost:7146",
    "http://127.0.0.1:7146",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Ocp-Apim-Subscription-Key", "X-User-Email", "X-App-Id"],
)

# -------------------------------------------------------------------
# Routes
# -------------------------------------------------------------------
from api.routes import health, support, widget

app.include_router(health.router)
app.include_router(support.router, prefix="/api")
app.include_router(widget.router, prefix="/api")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
