"""
Landing page route for support.acidni.net.

Serves an HTML page with the Zendesk Web Widget embedded for:
- Live chat support
- Ticket submission
- Help center access
- Ticket tracking (via Zendesk authentication)
"""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from api.config import get_settings

router = APIRouter(tags=["landing"])

settings = get_settings()


LANDING_PAGE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Acidni Support</title>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🎧</text></svg>">
    <style>
        :root {
            --primary: #0078d4;
            --primary-dark: #106ebe;
            --bg: #f5f5f5;
            --card-bg: #ffffff;
            --text: #323130;
            --text-muted: #605e5c;
            --border: #edebe9;
        }
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        body {
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg);
            color: var(--text);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        header {
            background: var(--primary);
            color: white;
            padding: 1rem 2rem;
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        header img {
            height: 40px;
        }
        header h1 {
            font-size: 1.5rem;
            font-weight: 600;
        }
        main {
            flex: 1;
            padding: 2rem;
            max-width: 1200px;
            margin: 0 auto;
            width: 100%;
        }
        .hero {
            text-align: center;
            padding: 3rem 1rem;
        }
        .hero h2 {
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }
        .hero p {
            color: var(--text-muted);
            font-size: 1.1rem;
        }
        .cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 1.5rem;
            margin-top: 2rem;
        }
        .card {
            background: var(--card-bg);
            border-radius: 8px;
            padding: 1.5rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        .card h3 {
            font-size: 1.25rem;
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        .card p {
            color: var(--text-muted);
            margin-bottom: 1rem;
        }
        .card a, .card button {
            display: inline-block;
            background: var(--primary);
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 4px;
            text-decoration: none;
            border: none;
            cursor: pointer;
            font-size: 0.9rem;
            font-weight: 500;
        }
        .card a:hover, .card button:hover {
            background: var(--primary-dark);
        }
        .products {
            margin-top: 3rem;
        }
        .products h3 {
            text-align: center;
            margin-bottom: 1rem;
            color: var(--text-muted);
        }
        .product-list {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 1rem;
        }
        .product-chip {
            background: var(--card-bg);
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 0.85rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        footer {
            text-align: center;
            padding: 1.5rem;
            color: var(--text-muted);
            font-size: 0.85rem;
            border-top: 1px solid var(--border);
        }
        footer a {
            color: var(--primary);
            text-decoration: none;
        }
        .icon {
            font-size: 1.5rem;
        }
        @media (max-width: 600px) {
            header {
                padding: 1rem;
            }
            .hero h2 {
                font-size: 1.5rem;
            }
            main {
                padding: 1rem;
            }
        }
    </style>
</head>
<body>
    <header>
        <span style="font-size: 2rem;">🅰️</span>
        <h1>Acidni Support</h1>
    </header>
    
    <main>
        <section class="hero">
            <h2>How can we help you today?</h2>
            <p>Get support for all Acidni products — chat with us, submit a ticket, or browse our help center.</p>
        </section>

        <div class="cards">
            <div class="card">
                <h3><span class="icon">💬</span> Live Chat</h3>
                <p>Chat with our support team in real-time. Available during business hours.</p>
                <button onclick="zE('messenger', 'open')">Start Chat</button>
            </div>

            <div class="card">
                <h3><span class="icon">🎫</span> Submit a Ticket</h3>
                <p>Create a support ticket and we'll respond within 24 hours.</p>
                <button onclick="zE('messenger', 'open'); zE('messenger:set', 'conversationFields', [{id: 'ticket', type: 'contact_form'}]);">New Ticket</button>
            </div>

            <div class="card">
                <h3><span class="icon">📚</span> Help Center</h3>
                <p>Browse FAQs, guides, and documentation for all products.</p>
                <a href="https://acidni.zendesk.com/hc" target="_blank">Browse Articles</a>
            </div>

            <div class="card">
                <h3><span class="icon">📋</span> My Tickets</h3>
                <p>View and track the status of your existing support requests.</p>
                <a href="https://acidni.zendesk.com/hc/requests" target="_blank">View My Tickets</a>
            </div>
        </div>

        <section class="products">
            <h3>Supported Products</h3>
            <div class="product-list">
                <span class="product-chip">🌿 Terprint</span>
                <span class="product-chip">🔬 RepoLens</span>
                <span class="product-chip">☀️ Solar</span>
                <span class="product-chip">⚡ GridSight</span>
                <span class="product-chip">🚶 StepSafe</span>
                <span class="product-chip">🎮 Minecraft Server</span>
                <span class="product-chip">🤖 AI SDO</span>
            </div>
        </section>
    </main>

    <footer>
        <p>© 2026 Acidni LLC • <a href="https://acidni.net">acidni.net</a> • <a href="/docs">API Docs</a> • <a href="/health">Status</a></p>
        <p style="margin-top: 0.5rem;">support.acidni.net v{VERSION}</p>
    </footer>

    <!-- Zendesk Web Widget -->
    <script id="ze-snippet" src="https://static.zdassets.com/ekr/snippet.js?key={ZENDESK_KEY}"></script>
    <script>
        // Configure Zendesk Widget
        window.zESettings = {
            webWidget: {
                color: { theme: '#0078d4' },
                contactForm: {
                    title: { '*': 'Contact Acidni Support' }
                },
                helpCenter: {
                    title: { '*': 'Acidni Help Center' }
                }
            }
        };
    </script>
</body>
</html>
"""


@router.get("/", response_class=HTMLResponse)
async def landing_page():
    """Serve the support portal landing page with Zendesk Web Widget."""
    zendesk_key = settings.zendesk_web_widget_key
    version = settings.app_version

    html = LANDING_PAGE_HTML.replace("{VERSION}", version)

    # Only include Zendesk widget if key is configured
    if zendesk_key:
        html = html.replace("{ZENDESK_KEY}", zendesk_key)
    else:
        # Remove Zendesk script if not configured, add fallback
        html = html.replace(
            '<!-- Zendesk Web Widget -->',
            '<!-- Zendesk Web Widget (not configured) -->'
        )
        html = html.replace(
            '<script id="ze-snippet" src="https://static.zdassets.com/ekr/snippet.js?key={ZENDESK_KEY}"></script>',
            '<!-- Zendesk widget key not configured -->'
        )
        html = html.replace(
            "onclick=\"zE('messenger', 'open')\"",
            'onclick="window.location.href=\'mailto:support@acidni.net\'"'
        )
        html = html.replace(
            "onclick=\"zE('messenger', 'open'); zE('messenger:set', 'conversationFields', [{id: 'ticket', type: 'contact_form'}]);\"",
            'onclick="window.location.href=\'mailto:support@acidni.net?subject=Support%20Request\'"'
        )

    return HTMLResponse(content=html)
