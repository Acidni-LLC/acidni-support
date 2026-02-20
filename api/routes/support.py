"""
Support routes — submit requests, get config, list tickets.
"""

import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException

from api.config import get_settings
from api.models import (
    SupportCategory,
    SupportSubmitRequest,
    SupportSubmitResponse,
    TicketDocument,
    WidgetBranding,
    WidgetCategory,
    WidgetConfig,
)
from api.services.cosmos_service import CosmosService
from api.services.devops_client import DevOpsClient
from api.services.routing_service import RoutingService

logger = logging.getLogger("acidni-support.routes.support")

router = APIRouter(tags=["support"])

# Lazy-init singletons
_routing: RoutingService | None = None
_devops: DevOpsClient | None = None
_cosmos: CosmosService | None = None

# Default widget categories
DEFAULT_CATEGORIES = [
    WidgetCategory(id="bug", label="Report a Bug", icon="🐛", devops_type="Bug"),
    WidgetCategory(id="feature", label="Request a Feature", icon="💡", devops_type="Task"),
    WidgetCategory(id="feedback", label="Give Feedback", icon="💬", devops_type="Task"),
    WidgetCategory(id="question", label="Ask a Question", icon="❓", devops_type="Task"),
]


def _get_routing() -> RoutingService:
    global _routing
    if _routing is None:
        _routing = RoutingService()
    return _routing


def _get_devops() -> DevOpsClient:
    global _devops
    if _devops is None:
        settings = get_settings()
        _devops = DevOpsClient(org_url=settings.devops_org_url, pat=settings.devops_pat)
    return _devops


def _get_cosmos() -> CosmosService:
    global _cosmos
    if _cosmos is None:
        _cosmos = CosmosService()
    return _cosmos


def _generate_ticket_id() -> str:
    """Generate a unique ticket ID: SUP-YYYYMMDD-HHMM-XXXX."""
    now = datetime.utcnow()
    import random
    suffix = f"{random.randint(1000, 9999)}"
    return f"SUP-{now.strftime('%Y%m%d')}-{now.strftime('%H%M')}-{suffix}"


@router.post("/submit", response_model=SupportSubmitResponse)
async def submit_support_request(request: SupportSubmitRequest) -> SupportSubmitResponse:
    """
    Submit a support request or feedback.

    Resolves the app_id to an Azure DevOps project, creates a work item,
    stores the ticket in Cosmos DB, and returns the work item reference.
    """
    routing = _get_routing()
    devops = _get_devops()
    cosmos = _get_cosmos()

    # 1. Resolve app_id to DevOps project
    route = routing.resolve(request.app_id)
    if route is None:
        route = routing.resolve("_default")
    if route is None:
        raise HTTPException(status_code=400, detail=f"Unknown app_id: {request.app_id}. No routing configured.")

    # 2. Determine work item type based on category
    category_type_map = {
        SupportCategory.BUG: "Bug",
        SupportCategory.FEATURE: "Task",
        SupportCategory.FEEDBACK: "Task",
        SupportCategory.QUESTION: "Task",
    }
    work_item_type = category_type_map.get(request.category, "Task")

    # 3. Build description HTML
    context_html = ""
    if request.context:
        ctx_items = []
        if request.context.url:
            ctx_items.append(f"<li><b>URL:</b> {request.context.url}</li>")
        if request.context.browser:
            ctx_items.append(f"<li><b>Browser:</b> {request.context.browser}</li>")
        if request.context.os:
            ctx_items.append(f"<li><b>OS:</b> {request.context.os}</li>")
        if request.context.app_version:
            ctx_items.append(f"<li><b>App Version:</b> {request.context.app_version}</li>")
        if request.context.screen_resolution:
            ctx_items.append(f"<li><b>Resolution:</b> {request.context.screen_resolution}</li>")
        if ctx_items:
            context_html = f"<h3>Context</h3><ul>{''.join(ctx_items)}</ul>"

    reporter_html = ""
    if request.user_email:
        reporter_html = f"<h3>Reported By</h3><p>{request.user_name or ''} ({request.user_email})</p>"

    description_html = (
        f"<h3>{'Customer Report' if request.category == SupportCategory.BUG else 'Customer Feedback'}</h3>"
        f"<p>{request.description}</p>"
        f"<h3>App</h3><p>{request.app_id} (routed to {route['devops_project']})</p>"
        f"{context_html}"
        f"{reporter_html}"
    )

    # 4. Tag prefix based on category
    tag_prefix = {
        SupportCategory.BUG: "support-widget; customer-reported",
        SupportCategory.FEATURE: "support-widget; feature-request",
        SupportCategory.FEEDBACK: "support-widget; customer-feedback",
        SupportCategory.QUESTION: "support-widget; customer-question",
    }
    tags = f"{tag_prefix.get(request.category, 'support-widget')}; {request.app_id}"

    # 5. Create work item in Azure DevOps
    title_prefix = {
        SupportCategory.BUG: "[Support]",
        SupportCategory.FEATURE: "[Feature Request]",
        SupportCategory.FEEDBACK: "[Feedback]",
        SupportCategory.QUESTION: "[Question]",
    }
    title = f"{title_prefix.get(request.category, '[Support]')} {request.subject}"

    try:
        work_item = await devops.create_work_item(
            project=route["devops_project"],
            work_item_type=work_item_type,
            title=title,
            description=description_html,
            area_path=route.get("area_path", route["devops_project"]),
            priority=request.priority,
            tags=tags,
        )
    except Exception:
        logger.exception("Failed to create DevOps work item for app_id=%s", request.app_id)
        raise HTTPException(status_code=502, detail="Failed to create work item in Azure DevOps")

    # 6. Generate ticket ID and store in Cosmos
    ticket_id = _generate_ticket_id()
    ticket = TicketDocument(
        id=ticket_id,
        app_id=request.app_id,
        category=request.category,
        subject=request.subject,
        description=request.description,
        priority=request.priority,
        user_email=request.user_email,
        user_name=request.user_name,
        context=request.context,
        devops={
            "org": "acidni",
            "project": route["devops_project"],
            "work_item_id": work_item["id"],
            "work_item_url": work_item["url"],
            "work_item_type": work_item_type,
        },
    )

    try:
        await cosmos.save_ticket(ticket)
    except Exception:
        logger.exception("Failed to save ticket %s to Cosmos DB", ticket_id)
        # Don't fail — work item was already created in DevOps

    logger.info(
        "Support ticket created: %s → %s #%s",
        ticket_id,
        route["devops_project"],
        work_item["id"],
    )

    return SupportSubmitResponse(
        ticket_id=ticket_id,
        devops_work_item_id=work_item["id"],
        devops_work_item_url=work_item["url"],
        status="created",
        message="Your support request has been submitted. We'll review it shortly.",
    )


@router.get("/config/{app_id}", response_model=WidgetConfig)
async def get_widget_config(app_id: str) -> WidgetConfig:
    """Return widget configuration for a specific app."""
    routing = _get_routing()
    route = routing.resolve(app_id)
    if route is None:
        route = routing.resolve("_default")
    if route is None:
        raise HTTPException(status_code=404, detail=f"No configuration found for app_id: {app_id}")

    return WidgetConfig(
        app_id=app_id,
        app_name=route.get("app_name", app_id),
        categories=DEFAULT_CATEGORIES,
        fields={"priority": True, "screenshot": True, "email": True},
        branding=WidgetBranding(),
        devops_project=route["devops_project"],
        area_path=route.get("area_path", route["devops_project"]),
    )


@router.get("/tickets")
async def list_user_tickets(
    app_id: str | None = None,
    email: str | None = None,
    limit: int = 25,
) -> list[dict]:
    """List past support tickets for a user/app, most recent first.

    Query params:
        app_id: Filter by application
        email:  Filter by submitter email
        limit:  Max results (default 25)
    """
    cosmos = _get_cosmos()
    tickets = await cosmos.list_tickets(app_id=app_id, user_email=email, limit=limit)
    # Return only safe fields (strip internal partition keys etc.)
    return [
        {
            "ticket_id": t["id"],
            "app_id": t.get("app_id"),
            "category": t.get("category"),
            "subject": t.get("subject"),
            "status": t.get("status", "created"),
            "priority": t.get("priority"),
            "created_at": t.get("created_at"),
            "devops_work_item_id": t.get("devops", {}).get("work_item_id") if t.get("devops") else None,
        }
        for t in tickets
    ]
