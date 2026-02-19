"""
Cosmos DB service — ticket storage and retrieval.
"""

import logging
from datetime import datetime

from azure.cosmos.aio import CosmosClient
from azure.identity.aio import DefaultAzureCredential

from api.config import get_settings
from api.models import TicketDocument

logger = logging.getLogger("acidni-support.services.cosmos")


class CosmosService:
    """Cosmos DB operations for support tickets."""

    def __init__(self) -> None:
        settings = get_settings()
        self._endpoint = settings.cosmos_endpoint
        self._database_name = settings.cosmos_database
        self._credential = DefaultAzureCredential()
        self._client: CosmosClient | None = None

    async def _get_container(self, container_name: str = "tickets"):
        """Get a Cosmos container client (lazy init)."""
        if self._client is None:
            self._client = CosmosClient(self._endpoint, credential=self._credential)
        db = self._client.get_database_client(self._database_name)
        return db.get_container_client(container_name)

    async def save_ticket(self, ticket: TicketDocument) -> dict:
        """Save a ticket document to the tickets container."""
        container = await self._get_container("tickets")
        doc = ticket.model_dump(mode="json")
        doc["_partition_key"] = ticket.app_id
        result = await container.upsert_item(doc)
        logger.info("Saved ticket %s to Cosmos DB", ticket.id)
        return result

    async def get_ticket(self, ticket_id: str, app_id: str) -> dict | None:
        """Retrieve a ticket by ID."""
        container = await self._get_container("tickets")
        try:
            item = await container.read_item(item=ticket_id, partition_key=app_id)
            return item
        except Exception:
            logger.warning("Ticket %s not found", ticket_id)
            return None

    async def list_tickets(
        self,
        app_id: str | None = None,
        user_email: str | None = None,
        limit: int = 50,
    ) -> list[dict]:
        """List tickets with optional filters."""
        container = await self._get_container("tickets")

        conditions = []
        params = []
        if app_id:
            conditions.append("c.app_id = @app_id")
            params.append({"name": "@app_id", "value": app_id})
        if user_email:
            conditions.append("c.user_email = @email")
            params.append({"name": "@email", "value": user_email})

        where_clause = f" WHERE {' AND '.join(conditions)}" if conditions else ""
        query = f"SELECT TOP {limit} * FROM c{where_clause} ORDER BY c.created_at DESC"

        items = []
        async for item in container.query_items(query=query, parameters=params or None):
            items.append(item)
        return items

    async def save_audit_log(self, ticket_id: str, app_id: str, action: str, details: dict) -> None:
        """Write an entry to the audit_log container."""
        container = await self._get_container("audit_log")
        doc = {
            "id": f"{ticket_id}-{action}-{datetime.utcnow().isoformat()}",
            "ticket_id": ticket_id,
            "app_id": app_id,
            "action": action,
            "details": details,
            "timestamp": datetime.utcnow().isoformat(),
            "_partition_key": app_id,
        }
        await container.upsert_item(doc)
        logger.info("Audit log: %s %s", action, ticket_id)

    async def close(self) -> None:
        """Close the Cosmos client."""
        if self._client:
            await self._client.close()
