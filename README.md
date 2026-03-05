# acidni-support

Unified support and feedback module for all Acidni LLC products. Provides an embeddable web component widget that collects support requests and routes them to the correct Azure DevOps project.

> **Integration Guide:** See [docs/integration-guide.md](docs/integration-guide.md) for full integration docs, widget attributes, API payloads, and framework examples.

## Architecture

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”     â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”     â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  Widget (JS)    â”‚ â”€â”€â–¶ â”‚  acidni-support API      â”‚ â”€â”€â–¶ â”‚ Azure DevOps â”‚
â”‚  Web Component  â”‚     â”‚  FastAPI + Python 3.12    â”‚     â”‚ Work Items   â”‚
â”‚  Shadow DOM     â”‚     â”‚  Container App            â”‚     â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜     â”‚                           â”‚     â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                        â”‚  POST /api/submit         â”‚ â”€â”€â–¶ â”‚ Cosmos DB    â”‚
                        â”‚  GET  /api/config/:id     â”‚     â”‚ Ticket Store â”‚
                        â”‚  GET  /api/widget.js      â”‚     â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                        â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

## Quick Start

### Embed in any web app

```html
<acidni-support
  app-id="terprint-web"
  api-url="https://api.acidni.net/support/api">
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
  api-url="https://api.acidni.net/support/api">
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
    api-url="https://api.acidni.net/support/api"
  />
);
```

**Static HTML**
```html
<acidni-support app-id="solar" position="bottom-left"
  api-url="https://api.acidni.net/support/api">
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
â”œâ”€â”€ api/
â”‚   â”œâ”€â”€ main.py                    # FastAPI application
â”‚   â”œâ”€â”€ config.py                  # Settings (pydantic-settings)
â”‚   â”œâ”€â”€ models.py                  # Pydantic models
â”‚   â”œâ”€â”€ routes/
â”‚   â”‚   â”œâ”€â”€ health.py              # Health check
â”‚   â”‚   â”œâ”€â”€ support.py             # Submit/config endpoints
â”‚   â”‚   â””â”€â”€ widget.py              # Widget serving
â”‚   â”œâ”€â”€ services/
â”‚   â”‚   â”œâ”€â”€ routing_service.py     # Appâ†’DevOps routing
â”‚   â”‚   â”œâ”€â”€ devops_client.py       # Azure DevOps API
â”‚   â”‚   â”œâ”€â”€ cosmos_service.py      # Cosmos DB storage
â”‚   â”‚   â””â”€â”€ notification_service.py
â”‚   â””â”€â”€ config/
â”‚       â””â”€â”€ support-routing.yaml   # Appâ†’project mapping
â”œâ”€â”€ widget/
â”‚   â”œâ”€â”€ src/
â”‚   â”‚   â”œâ”€â”€ index.ts               # Web component
â”‚   â”‚   â””â”€â”€ styles.ts              # Shadow DOM CSS
â”‚   â”œâ”€â”€ package.json
â”‚   â”œâ”€â”€ rollup.config.mjs
â”‚   â””â”€â”€ tsconfig.json
â”œâ”€â”€ Dockerfile
â”œâ”€â”€ pyproject.toml
â””â”€â”€ .github/workflows/deploy.yml
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
