# acidni-support

Unified support and feedback module for all Acidni LLC products. Provides an embeddable web component widget that collects support requests and routes them to the correct Azure DevOps project.

> **Integration Guide:** See [docs/integration-guide.md](docs/integration-guide.md) for full integration docs, widget attributes, API payloads, and framework examples.

## Architecture

```
┌─────────────────┐     ┌─────────────────────────┐     ┌──────────────┐
│  Widget (JS)    │ ──▶ │  acidni-support API      │ ──▶ │ Azure DevOps │
│  Web Component  │     │  FastAPI + Python 3.12    │     │ Work Items   │
│  Shadow DOM     │     │  Container App            │     └──────────────┘
└─────────────────┘     │                           │     ┌──────────────┐
                        │  POST /api/submit         │ ──▶ │ Cosmos DB    │
                        │  GET  /api/config/:id     │     │ Ticket Store │
                        │  GET  /api/widget.js      │     └──────────────┘
                        └─────────────────────────────┘
```

## Quick Start

### Embed in any web app

```html
<acidni-support
  app-id="terprint-web"
  api-url="https://apim-terprint-dev.azure-api.net/support/api">
</acidni-support>
<script src="https://support.acidni.net/api/widget.js"></script>
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
<script src="https://support.acidni.net/api/widget.js"></script>
<acidni-support app-id="terprint-web"
  api-url="https://apim-terprint-dev.azure-api.net/support/api">
</acidni-support>
```

**React/Next.js**
```tsx
useEffect(() => {
  const script = document.createElement('script');
  script.src = 'https://support.acidni.net/api/widget.js';
  document.body.appendChild(script);
}, []);
return (
  <acidni-support
    app-id="gridsight"
    api-url="https://apim-terprint-dev.azure-api.net/support/api"
  />
);
```

**Static HTML**
```html
<acidni-support app-id="solar" position="bottom-left"
  api-url="https://apim-terprint-dev.azure-api.net/support/api">
</acidni-support>
<script src="https://support.acidni.net/api/widget.js"></script>
```

**Teams Tab (iframe)**
```html
<iframe src="https://support.acidni.net/api/embed?app-id=acidni-sdo"
        width="400" height="600" frameBorder="0"></iframe>
```

## API Endpoints

All API paths are relative to the base URL. Through APIM prefix `/support`:

| Method | Path | APIM URL | Description |
|--------|------|----------|-------------|
| POST | `/api/submit` | `/support/api/submit` | Submit a support request |
| GET | `/api/config/{app_id}` | `/support/api/config/{app_id}` | Get widget config for an app |
| GET | `/api/widget.js` | `/support/api/widget.js` | Serve widget JS bundle |
| GET | `/api/embed` | `/support/api/embed` | Embeddable HTML page |
| GET | `/health` | `/support/health` | Health check |

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
