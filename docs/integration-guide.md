# acidni-support Integration Guide

Complete guide for integrating the Acidni support widget into any Acidni product.

---

## Table of Contents

- [Overview](#overview)
- [Quick Start (2 lines of HTML)](#quick-start)
- [Widget Attributes](#widget-attributes)
- [Available app-id Values](#available-app-id-values)
- [Framework Integration Examples](#framework-integration-examples)
  - [Blazor Server (.NET)](#blazor-server-net)
  - [React / Next.js](#react--nextjs)
  - [Static HTML / Astro / Hugo](#static-html)
  - [Teams Tab (iframe)](#teams-tab-iframe)
  - [Angular](#angular)
  - [Vue.js](#vuejs)
- [Direct API Usage](#direct-api-usage)
  - [Submit a Ticket](#submit-a-ticket)
  - [Get Widget Config](#get-widget-config)
- [API Reference](#api-reference)
- [Widget Behavior](#widget-behavior)
- [Styling & Positioning](#styling--positioning)
- [CORS Allowed Origins](#cors-allowed-origins)
- [Troubleshooting](#troubleshooting)

---

## Overview

`acidni-support` is a centralized support widget deployed as a web component. When a user submits feedback or a bug report, the widget:

1. Sends the request to the acidni-support API
2. Routes it to the correct **Azure DevOps project** based on the `app-id`
3. Creates a **work item** (Bug or User Story) with full context
4. Stores a ticket record in **Cosmos DB** for tracking

The widget is served as a single JavaScript file that registers a `<acidni-support>` custom element. It uses Shadow DOM for style isolation — it will not conflict with your app's CSS.

---

## Quick Start

Add these two lines to any HTML page:

```html
<acidni-support
  app-id="YOUR-APP-ID"
  api-url="https://apim-terprint-dev.azure-api.net/support/api">
</acidni-support>
<script src="https://support.acidni.net/api/widget.js"></script>
```

Replace `YOUR-APP-ID` with your product's app ID from the [table below](#available-app-id-values).

That's it. A support button appears in the bottom-right corner.

---

## Widget Attributes

| Attribute | Required | Default | Description |
| --------- | -------- | ------- | ----------- |
| `app-id` | **Yes** | — | Your product's identifier. Must match an entry in `support-routing.yaml`. |
| `api-url` | No | `https://apim-terprint-dev.azure-api.net/support/api` | Base URL for the support API. The widget appends `/submit` and `/config/{app_id}` to this. |
| `position` | No | `bottom-right` | Where the floating action button appears. Options: `bottom-right`, `bottom-left`, `inline`. |

### Position Options

| Value | Behavior |
| ----- | -------- |
| `bottom-right` | Fixed FAB in the bottom-right corner (default) |
| `bottom-left` | Fixed FAB in the bottom-left corner |
| `inline` | No FAB — the support panel renders inline where the element is placed |

---

## Available app-id Values

Use the `app-id` that matches your product. Each one routes to the correct Azure DevOps project and area path.

### Terprint Platform

| app-id | App Name | DevOps Project | Area Path |
| ------ | -------- | -------------- | --------- |
| `terprint-web` | Terprint | Terprint | Terprint\Web |
| `terprint-ai-chat` | Terprint AI Chat | Terprint | Terprint\AI Services\Chat |
| `terprint-ai-recommender` | Terprint AI Recommender | Terprint | Terprint\AI Services\Recommender |
| `terprint-ai-deals` | Terprint AI Deals | Terprint | Terprint\AI Services |
| `terprint-ai-lab` | Terprint AI Lab | Terprint | Terprint\AI Services |
| `terprint-ai-health` | Terprint AI Health | Terprint | Terprint\AI Services |
| `terprint-doctor-portal` | Doctor Portal | Terprint | Terprint\Web |

### Other Products

| app-id | App Name | DevOps Project |
| ------ | -------- | -------------- |
| `cdes` | CDES | CDES |
| `acidni-sdo` | AI SDO | Acidni-SDO |
| `acidni-repolens` | RepoLens | Acidni-SDO |
| `solar` | Solar Portal | SolarReporting |
| `gridsight` | GridSight | GridSight |
| `mobilemech` | MobileMech | MobileMech |
| `fl-wetlands` | FL Wetlands Monitor | FLWetlands |
| `donate` | Donate | Donate |
| `chat-analyzer` | ChatAnalyzer | ChatAnalyzer |
| `text-a-truck` | Text A Truck | TextATruck |
| `veterans-build` | VeteransBuild | VeteransBuild |
| `minecraft` | Minecraft Server | Minecraft |
| `devtools` | DevTools | DevTools |
| `gowild-finder` | GoWild Finder | GoWild Finder |
| `stepsafe` | StepSafe AI | StepSafe AI |

### Special

| app-id | Purpose |
| ------ | ------- |
| `acidni-support` | Self — for bugs in the support widget itself |
| `infrastructure` | Internal infrastructure issues |

> **Don't see your app?** Add a new entry to `api/config/support-routing.yaml` in the [acidni-support repo](https://github.com/Acidni-LLC/acidni-support). Any unrecognized `app-id` falls back to the `_default` route (Terprint project).

---

## Framework Integration Examples

### Blazor Server (.NET)

Add to your `_Host.cshtml` or `App.razor` layout:

```html
<!-- At the bottom of <body>, before </body> -->
<acidni-support app-id="terprint-web"
  api-url="https://apim-terprint-dev.azure-api.net/support/api">
</acidni-support>
<script src="https://support.acidni.net/api/widget.js"></script>
```

No NuGet packages needed. The web component registers itself.

### React / Next.js

```tsx
// components/SupportWidget.tsx
"use client";
import { useEffect } from "react";

export default function SupportWidget({ appId }: { appId: string }) {
  useEffect(() => {
    // Load widget script once
    if (!document.querySelector('script[src*="acidni-support"]')) {
      const script = document.createElement("script");
      script.src = "https://support.acidni.net/api/widget.js";
      script.async = true;
      document.body.appendChild(script);
    }
  }, []);

  return (
    <acidni-support
      app-id={appId}
      api-url="https://apim-terprint-dev.azure-api.net/support/api"
    />
  );
}

// TypeScript: declare the custom element
declare global {
  namespace JSX {
    interface IntrinsicElements {
      "acidni-support": React.DetailedHTMLProps<
        React.HTMLAttributes<HTMLElement> & {
          "app-id"?: string;
          "api-url"?: string;
          position?: string;
        },
        HTMLElement
      >;
    }
  }
}
```

Then in your layout or page:

```tsx
import SupportWidget from "@/components/SupportWidget";

export default function Layout({ children }) {
  return (
    <html>
      <body>
        {children}
        <SupportWidget appId="gridsight" />
      </body>
    </html>
  );
}
```

### Static HTML

```html
<!DOCTYPE html>
<html>
<head><title>My App</title></head>
<body>
  <!-- Your app content -->

  <!-- Support widget — add before </body> -->
  <acidni-support app-id="solar" position="bottom-left"
    api-url="https://apim-terprint-dev.azure-api.net/support/api">
  </acidni-support>
  <script src="https://support.acidni.net/api/widget.js"></script>
</body>
</html>
```

### Teams Tab (iframe)

For Teams tabs that can't load external scripts, use the embed endpoint:

```html
<iframe
  src="https://support.acidni.net/api/embed?app-id=acidni-sdo"
  width="400"
  height="600"
  frameBorder="0"
  title="Support">
</iframe>
```

### Angular

```typescript
// app.component.ts
import { Component, CUSTOM_ELEMENTS_SCHEMA } from "@angular/core";

@Component({
  selector: "app-root",
  template: `
    <router-outlet></router-outlet>
    <acidni-support
      app-id="gridsight"
      api-url="https://apim-terprint-dev.azure-api.net/support/api">
    </acidni-support>
  `,
  schemas: [CUSTOM_ELEMENTS_SCHEMA],
})
export class AppComponent {}
```

Add the script to `angular.json`:

```json
{
  "architect": {
    "build": {
      "options": {
        "scripts": [
          { "input": "https://support.acidni.net/api/widget.js", "inject": true }
        ]
      }
    }
  }
}
```

Or load it in `index.html`:

```html
<script src="https://support.acidni.net/api/widget.js"></script>
```

### Vue.js

```vue
<!-- App.vue or layout component -->
<template>
  <div id="app">
    <router-view />
    <acidni-support
      app-id="mobilemech"
      api-url="https://apim-terprint-dev.azure-api.net/support/api"
    />
  </div>
</template>

<script setup>
import { onMounted } from 'vue';

onMounted(() => {
  if (!document.querySelector('script[src*="acidni-support"]')) {
    const s = document.createElement('script');
    s.src = 'https://support.acidni.net/api/widget.js';
    s.async = true;
    document.body.appendChild(s);
  }
});
</script>
```

Add to `vite.config.ts` to suppress unknown element warnings:

```typescript
export default defineConfig({
  plugins: [
    vue({
      template: {
        compilerOptions: {
          isCustomElement: (tag) => tag === "acidni-support",
        },
      },
    }),
  ],
});
```

---

## Direct API Usage

If your app needs to submit tickets programmatically (without the widget), call the API directly.

### Base URLs

| Channel | Base URL |
| ------- | -------- |
| **Through APIM** (recommended) | `https://apim-terprint-dev.azure-api.net/support/api` |
| **Direct** | `https://support.acidni.net/api` |

> APIM requires an `Ocp-Apim-Subscription-Key` header. Direct access does not.

### Submit a Ticket

```http
POST /api/submit
Content-Type: application/json
```

**Request Body:**

```json
{
  "app_id": "terprint-web",
  "category": "bug",
  "subject": "Dashboard chart not loading",
  "description": "When I navigate to the Terpene Radar chart on the dashboard, it shows a spinning loader indefinitely. Happens in Chrome 120 on Windows 11.",
  "priority": 2,
  "user_email": "user@example.com",
  "user_name": "Jane Doe",
  "context": {
    "url": "https://terprint.acidni.net/dashboard",
    "browser": "Chrome/120.0.0.0",
    "os": "Windows 11",
    "screen_resolution": "1920x1080",
    "app_version": "4.5.0"
  }
}
```

**Field Reference:**

| Field | Type | Required | Constraints | Description |
| ----- | ---- | -------- | ----------- | ----------- |
| `app_id` | string | **Yes** | Must match routing config | Product identifier |
| `category` | enum | **Yes** | `bug`, `feature`, `feedback`, `question` | Type of request |
| `subject` | string | **Yes** | 5–200 chars | Brief summary |
| `description` | string | **Yes** | 10–5000 chars | Detailed description |
| `priority` | int | No | 1–4 (default: 3) | 1=Critical, 2=High, 3=Normal, 4=Low |
| `user_email` | string | No | Valid email | Submitter's email |
| `user_name` | string | No | — | Submitter's name |
| `context` | object | No | — | Auto-captured client context |
| `context.url` | string | No | — | Current page URL |
| `context.browser` | string | No | — | User agent string |
| `context.os` | string | No | — | Operating system |
| `context.screen_resolution` | string | No | — | e.g. `1920x1080` |
| `context.app_version` | string | No | — | App version tag |
| `screenshot_base64` | string | No | Max 7MB | Base64-encoded screenshot |

**Response (201 Created):**

```json
{
  "ticket_id": "SUP-20260219-2206-9156",
  "devops_work_item_id": 971,
  "devops_work_item_url": "https://dev.azure.com/acidni/Terprint/_workitems/edit/971",
  "status": "created",
  "message": "Your support request has been submitted. We'll review it shortly."
}
```

**Error Responses:**

| Status | Meaning |
| ------ | ------- |
| 400 | Validation error (bad payload) |
| 422 | Unprocessable entity (missing required fields) |
| 500 | Internal error (DevOps API or Cosmos failure) |

### Category → Work Item Type Mapping

| Category | DevOps Work Item Type |
| -------- | -------------------- |
| `bug` | Bug |
| `feature` | User Story |
| `feedback` | User Story |
| `question` | User Story |

### Get Widget Config

```http
GET /api/config/{app_id}
```

Returns the widget configuration for a given app, including available categories and branding.

**Example Response:**

```json
{
  "app_id": "terprint-web",
  "app_name": "Terprint",
  "categories": [
    { "id": "bug", "label": "Report a Bug", "icon": "🐛", "devops_type": "Bug" },
    { "id": "feature", "label": "Request a Feature", "icon": "💡", "devops_type": "User Story" },
    { "id": "feedback", "label": "General Feedback", "icon": "💬", "devops_type": "User Story" },
    { "id": "question", "label": "Ask a Question", "icon": "❓", "devops_type": "User Story" }
  ],
  "fields": { "email": true, "priority": true, "screenshot": false },
  "branding": {
    "primary_color": "#2563eb",
    "logo_url": null,
    "position": "bottom-right"
  },
  "devops_project": "Terprint",
  "area_path": "Terprint\\Web"
}
```

---

## API Reference

All paths are relative to the service root. Through APIM, prepend `/support`.

| Method | Path | Description |
| ------ | ---- | ----------- |
| `POST` | `/api/submit` | Submit a support request → creates DevOps work item |
| `GET` | `/api/config/{app_id}` | Get widget config (categories, branding) for an app |
| `GET` | `/api/widget.js` | Serve the compiled widget JavaScript bundle |
| `GET` | `/api/widget.css` | Serve widget CSS (if external) |
| `GET` | `/api/embed` | Embeddable HTML page (for iframes) |
| `GET` | `/health` | Health check (returns `{ status, version, environment }`) |

---

## Widget Behavior

### User Flow

1. User clicks the **floating action button** (chat bubble icon)
2. A panel opens showing **support categories** (Bug, Feature, Feedback, Question)
3. User selects a category → a form appears with Subject, Description, Email, Priority
4. User submits → the widget shows a **success message** with the ticket ID
5. The form closes (or resets for inline mode)

### What Gets Captured Automatically

The widget captures client context without user input:

- **Current page URL** (`window.location.href`)
- **Browser user agent** (`navigator.userAgent`)
- **Screen resolution** (`window.screen.width x height`)

### Shadow DOM

The widget uses Shadow DOM, which means:

- Widget styles do **not** leak into your app
- Your app styles do **not** affect the widget
- No CSS conflicts regardless of your framework

---

## Styling & Positioning

### Inline Mode

Use `position="inline"` to embed the panel directly in your page layout instead of a floating button:

```html
<div class="support-section">
  <h2>Need Help?</h2>
  <acidni-support app-id="terprint-web" position="inline"
    api-url="https://apim-terprint-dev.azure-api.net/support/api">
  </acidni-support>
</div>
```

### CSS Custom Properties (Future)

Custom theming via CSS custom properties is planned. Currently, branding colors come from the `/api/config/{app_id}` response.

---

## CORS Allowed Origins

The API allows requests from these origins. If your app is hosted on a different domain, request an addition via a support ticket or PR.

**Allowed:**

- `https://*.acidni.net` (all product subdomains)
- `https://www.cdes.world`
- `https://sales.terprint.com`
- `https://teams.microsoft.com`
- `http://localhost:3000` / `:5000` / `:7146` (local dev)

---

## Troubleshooting

### Widget doesn't appear

1. Check browser console for errors
2. Verify the script loaded: `document.querySelector('acidni-support')` should return an element
3. Verify `app-id` is set — the widget won't render without it
4. Check network tab for `widget.js` request — should return 200

### "Failed to load config" warning in console

- The widget tries to fetch `/config/{app_id}` on load
- If the `app-id` isn't in `support-routing.yaml`, it falls back to `_default`
- Check that `api-url` is correct and the API is reachable

### Ticket submitted but no work item created

- Check the API response — if `devops_work_item_id` is present, it was created
- Verify the DevOps project in `support-routing.yaml` exists
- Check API logs: `az containerapp logs show --name ca-acidni-support --resource-group rg-dev-terprint-ca --tail 50`

### CORS error in browser

- Your origin is not in the allowed list
- Add it to `ALLOWED_ORIGINS` in `api/main.py` and redeploy
- Or submit a PR / create a work item to request it

---

## Adding a New Product

To add support for a new Acidni product:

1. Add an entry to `api/config/support-routing.yaml`:

   ```yaml
   - app_id: my-new-app
     app_name: My New App
     devops_project: MyProject
     area_path: "MyProject"
   ```

2. Add the origin to `ALLOWED_ORIGINS` in `api/main.py` if it's on a new domain

3. Commit, push, and let CI/CD deploy

4. Add the widget to your app:

   ```html
   <acidni-support app-id="my-new-app"
     api-url="https://apim-terprint-dev.azure-api.net/support/api">
   </acidni-support>
   <script src="https://support.acidni.net/api/widget.js"></script>
   ```

---

## Infrastructure Reference

| Resource | Value |
| -------- | ----- |
| Container App | `ca-acidni-support` |
| Resource Group | `rg-dev-terprint-ca` |
| APIM Route | `/support/*` |
| Cosmos DB | `acidni-cosmos-dev` / `support-dev` |
| DNS | `support.acidni.net` |
| ACR Image | `crterprint.azurecr.io/acidni-support` |
| GitHub Repo | [Acidni-LLC/acidni-support](https://github.com/Acidni-LLC/acidni-support) |
| Health Check | `https://support.acidni.net/health` |
| API Docs (dev) | `https://support.acidni.net/docs` |

---

acidni-support v1.0.0
