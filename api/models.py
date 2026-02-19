"""
Pydantic models for acidni-support API.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class SupportCategory(str, Enum):
    """Support request categories."""

    BUG = "bug"
    FEATURE = "feature"
    FEEDBACK = "feedback"
    QUESTION = "question"


class SubmitContext(BaseModel):
    """Client-side context captured automatically by the widget."""

    url: str | None = None
    browser: str | None = None
    os: str | None = None
    screen_resolution: str | None = None
    app_version: str | None = None


class SupportSubmitRequest(BaseModel):
    """Incoming support/feedback request from the widget."""

    app_id: str = Field(..., description="CMDB CI ID of the app (e.g. APP-000001)")
    category: SupportCategory = Field(..., description="Type of request")
    subject: str = Field(..., min_length=5, max_length=200, description="Brief summary")
    description: str = Field(..., min_length=10, max_length=5000, description="Detailed description")
    priority: int = Field(default=3, ge=1, le=4, description="Priority 1 (critical) to 4 (low)")
    user_email: str | None = Field(default=None, description="Submitter email")
    user_name: str | None = Field(default=None, description="Submitter name")
    context: SubmitContext | None = Field(default=None, description="Auto-captured context")
    screenshot_base64: str | None = Field(default=None, max_length=7_000_000, description="Optional screenshot")


class DevOpsInfo(BaseModel):
    """Azure DevOps work item reference."""

    org: str
    project: str
    work_item_id: int
    work_item_url: str
    work_item_type: str


class SupportSubmitResponse(BaseModel):
    """Response after successfully creating a support ticket."""

    ticket_id: str
    devops_work_item_id: int
    devops_work_item_url: str
    status: str = "created"
    message: str = "Your support request has been submitted. We'll review it shortly."


class TicketDocument(BaseModel):
    """Cosmos DB ticket document."""

    id: str
    app_id: str
    category: SupportCategory
    subject: str
    description: str
    priority: int
    status: str = "created"
    user_email: str | None = None
    user_name: str | None = None
    context: SubmitContext | None = None
    devops: DevOpsInfo | None = None
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")


class WidgetCategory(BaseModel):
    """Widget category configuration."""

    id: str
    label: str
    icon: str
    devops_type: str


class WidgetBranding(BaseModel):
    """Widget branding configuration."""

    primary_color: str = "#2563eb"
    logo_url: str | None = None
    position: str = "bottom-right"


class WidgetConfig(BaseModel):
    """Per-app widget configuration returned to the client."""

    app_id: str
    app_name: str
    categories: list[WidgetCategory]
    fields: dict[str, bool]
    branding: WidgetBranding
    devops_project: str
    area_path: str


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "healthy"
    version: str
    environment: str
    service: str = "acidni-support"
