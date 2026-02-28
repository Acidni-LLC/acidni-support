"""
Widget route — serves the embeddable JavaScript widget.
"""

import logging
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse, HTMLResponse

logger = logging.getLogger("acidni-support.routes.widget")

router = APIRouter(tags=["widget"])

WIDGET_DIR = Path(__file__).parent.parent.parent / "widget" / "dist"


@router.get("/widget.js", response_class=FileResponse)
async def serve_widget_js() -> FileResponse:
    """Serve the compiled support widget JavaScript bundle."""
    js_path = WIDGET_DIR / "acidni-support-widget.js"
    if not js_path.exists():
        logger.error("Widget JS not found at %s", js_path)
        return HTMLResponse(
            content="// Widget not built yet. Run: cd widget && npm run build",
            status_code=404,
            media_type="application/javascript",
        )
    return FileResponse(
        path=str(js_path),
        media_type="application/javascript",
        headers={
            "Cache-Control": "public, max-age=3600",
            "Access-Control-Allow-Origin": "*",
        },
    )


@router.get("/widget.css", response_class=FileResponse)
async def serve_widget_css() -> FileResponse:
    """Serve the widget CSS (if external)."""
    css_path = WIDGET_DIR / "acidni-support-widget.css"
    if not css_path.exists():
        return HTMLResponse(
            content="/* Widget CSS not built yet */",
            status_code=404,
            media_type="text/css",
        )
    return FileResponse(
        path=str(css_path),
        media_type="text/css",
        headers={
            "Cache-Control": "public, max-age=3600",
            "Access-Control-Allow-Origin": "*",
        },
    )


@router.get("/widget/embed", response_class=HTMLResponse)
async def widget_embed_page(
    app_id: str = "acidni-support-embed",
    user_email: str | None = None,
    user_name: str | None = None,
) -> HTMLResponse:
    """Return minimal HTML page embedding the widget — useful for iframes in Teams.

    Teams static tabs load this page via:
        https://support.acidni.net/api/widget/embed?app_id=<app_id>

    Query params:
        app_id:     The application identifier for support ticket routing.
        user_email: Pre-populate with the user's email address.
        user_name:  Pre-populate with the user's display name.

    NOTE: Teams may not resolve ``{loginHint}`` URL placeholders in static
    tab contentUrls. This page includes the Teams JS SDK and falls back
    to ``app.getContext()`` to obtain the user's login hint / UPN at
    runtime when the URL parameter is missing or unresolved.
    """
    # Detect unresolved Teams URL placeholders
    _TEAMS_PLACEHOLDERS = {"{loginHint}", "{userPrincipalName}", "{upn}"}
    resolved_email = user_email if user_email and user_email not in _TEAMS_PLACEHOLDERS else None
    resolved_name = user_name if user_name and user_name not in _TEAMS_PLACEHOLDERS else None

    # Build optional data attributes for pre-population
    extra_attrs = ""
    if resolved_email:
        extra_attrs += f' user-email="{resolved_email}"'
    if resolved_name:
        extra_attrs += f' user-name="{resolved_name}"'

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Acidni Support</title>
    <style>
        body {{ margin: 0; padding: 0; font-family: system-ui, -apple-system, sans-serif; background: transparent; }}
    </style>
</head>
<body>
    <acidni-support id="support-widget" app-id="{app_id}" api-url="https://support.acidni.net/api" position="inline"{extra_attrs}></acidni-support>
    <script src="/api/widget.js"></script>
    <script src="https://res.cdn.office.net/teams-js/2.31.1/js/MicrosoftTeams.min.js"></script>
    <script>
    (async function() {{
        // If email was already resolved from URL params, nothing to do
        var widget = document.getElementById('support-widget');
        if (widget && widget.getAttribute('user-email')) return;

        // Try Teams SDK context resolution
        try {{
            if (typeof microsoftTeams !== 'undefined') {{
                await microsoftTeams.app.initialize();
                var ctx = await microsoftTeams.app.getContext();
                var email = (ctx.user && ctx.user.loginHint) ||
                            (ctx.user && ctx.user.userPrincipalName) || '';
                var name = (ctx.user && ctx.user.displayName) || '';
                if (widget && email) {{
                    widget.setAttribute('user-email', email);
                }}
                if (widget && name && !widget.getAttribute('user-name')) {{
                    widget.setAttribute('user-name', name);
                }}
            }}
        }} catch (e) {{
            console.warn('[acidni-support] Teams SDK context unavailable:', e);
        }}
    }})();
    </script>
</body>
</html>"""
    return HTMLResponse(content=html)
