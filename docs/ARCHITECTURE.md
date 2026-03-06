# Acidni Support — Architecture

> Unified support and feedback module — embeddable web component widget for all Acidni products.

## System Overview

```text
┌─────────────────────────────────────────────┐
│              Any Acidni Product              │
│  ┌────────────────────────────────────────┐  │
│  │  <acidni-support> Web Component       │  │
│  │  (TypeScript, Shadow DOM)             │  │
│  └───────────────────┬────────────────────┘  │
└──────────────────────┼──────────────────────┘
                       │ POST /api/feedback
                       ▼
              ┌────────────────┐
              │  FastAPI       │
              │  Backend       │
              │  (Python)      │
              └───────┬────────┘
                      │
         ┌────────────┼────────────┐
         ▼            ▼            ▼
   ┌──────────┐ ┌──────────┐ ┌──────────┐
   │ Azure    │ │ App      │ │ Azure    │
   │ DevOps   │ │ Registry │ │ APIM     │
   │ (Work    │ │ (CMDB    │ │ (Route)  │
   │  Items)  │ │  Lookup) │ │          │
   └──────────┘ └──────────┘ └──────────┘
```

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Widget | TypeScript Web Component (Shadow DOM) |
| Backend | Python 3.12+ / FastAPI |
| Container | Docker → Azure Container Apps |
| Routing | Azure APIM |
| Work Items | Azure DevOps REST API |
| App Lookup | App Registry (CMDB) |
| CI/CD | GitHub Actions (1 workflow) |

## Project Structure

| Directory | Purpose |
|-----------|---------|
| `widget/` | TypeScript web component — `<acidni-support>` custom element |
| `api/` | FastAPI backend — receives feedback, creates DevOps work items |
| `tests/` | Test suite |
| `docs/` | Documentation |

## How It Works

1. User clicks support widget in any Acidni product
2. Widget collects: bug report / feature request / feedback / question
3. Widget POSTs to FastAPI backend via APIM
4. Backend looks up the source app in App Registry (CMDB)
5. Creates Azure DevOps work item in the correct project and area path
6. Returns confirmation to user

## Integration

Embed in any Acidni web app:

```html
<script src="https://support.acidni.net/widget.js"></script>
<acidni-support app-id="APP-000002"></acidni-support>
```

## CMDB Reference

Product code: `asup` | CI ID: `SVC-000001` | Status: development
