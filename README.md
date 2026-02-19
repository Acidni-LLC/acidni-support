# acidni-support

Unified support and feedback module for all Acidni LLC products. Provides an embeddable web component widget that collects support requests and routes them to the correct Azure DevOps project.

## Architecture

```
┌─────────────────┐     ┌─────────────────────────┐     ┌──────────────┐
│  Widget (JS)    │ ──▶ │  acidni-support API      │ ──▶ │ Azure DevOps │
│  Web Component  │     │  FastAPI + Python 3.12    │     │ Work Items   │
│  Shadow DOM     │     │  Container App            │     └──────────────┘
└─────────────────┘     │                           │     ┌──────────────┐
                        │  POST /support/submit     │ ──▶ │ Cosmos DB    │
                        │  GET  /support/config/:id │     │ Ticket Store │
                        │  GET  /widget/widget.js   │     └──────────────┘
                        └─────────────────────────────┘
```

## Quick Start

### Embed in any web app

```html
<acidni-support
  app-id="terprint-web"
  api-url="https://apim-terprint-dev.azure-api.net/support">
</acidni-support>
<script src="https://support.acidni.net/widget/widget.js"></script>
```

### Local Development

```bash
# 1. Clone
git clone https://github.com/Acidni-LLC/acidni-support.git
cd acidni-support

# 2. Install Python deps
pip install -e ".[dev]"

# 3. Build widget
cd widget && npm install && npm run build && cd ..

# 4. Configure
cp .env.example .env
# Edit .env with your Azure DevOps PAT

# 5. Run
uvicorn api.main:app --reload --port 8000
```

### Integration Examples

**Blazor Server (.NET)**
```html
<script src="https://support.acidni.net/widget/widget.js"></script>
<acidni-support app-id="terprint-web"></acidni-support>
```

**React/Next.js**
```tsx
useEffect(() => {
  const script = document.createElement('script');
  script.src = 'https://support.acidni.net/widget/widget.js';
  document.body.appendChild(script);
}, []);
return <acidni-support app-id="gridsight" />;
```

**Static HTML**
```html
<acidni-support app-id="solar" position="bottom-left"></acidni-support>
<script src="https://support.acidni.net/widget/widget.js"></script>
```

**Teams Tab (iframe)**
```html
<iframe src="https://support.acidni.net/widget/embed?app-id=acidni-sdo"
        width="400" height="600" frameBorder="0"></iframe>
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/support/submit` | Submit a support request |
| GET | `/support/config/{app_id}` | Get widget config for an app |
| GET | `/widget/widget.js` | Serve widget JS bundle |
| GET | `/widget/embed` | Embeddable HTML page |
| GET | `/health` | Health check |

## Project Structure

```
acidni-support/
├── api/
│   ├── main.py                    # FastAPI application
│   ├── config.py                  # Settings (pydantic-settings)
│   ├── models.py                  # Pydantic models
│   ├── routes/
│   │   ├── health.py              # Health check
│   │   ├── support.py             # Submit/config endpoints
│   │   └── widget.py              # Widget serving
│   ├── services/
│   │   ├── routing_service.py     # App→DevOps routing
│   │   ├── devops_client.py       # Azure DevOps API
│   │   ├── cosmos_service.py      # Cosmos DB storage
│   │   └── notification_service.py
│   └── config/
│       └── support-routing.yaml   # App→project mapping
├── widget/
│   ├── src/
│   │   ├── index.ts               # Web component
│   │   └── styles.ts              # Shadow DOM CSS
│   ├── package.json
│   ├── rollup.config.mjs
│   └── tsconfig.json
├── Dockerfile
├── pyproject.toml
└── .github/workflows/deploy.yml
```

## Infrastructure

| Resource | Name |
|----------|------|
| Container App | `ca-acidni-support` |
| APIM Route | `/support/*` |
| Cosmos DB | `acidni-cosmos-dev` / `support-dev` |
| DNS | `support.acidni.net` |
| ACR Image | `crterprint.azurecr.io/acidni-support` |

acidni-support v20260201-1430
