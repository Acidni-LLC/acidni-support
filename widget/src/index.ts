/**
 * acidni-support-widget — Embeddable support web component.
 *
 * Usage:
 *   <acidni-support app-id="terprint-web" api-url="https://apim-terprint-dev.azure-api.net/support"></acidni-support>
 *   <script src="https://support.acidni.net/widget/widget.js"></script>
 */

import { WIDGET_STYLES } from "./styles";

interface WidgetConfig {
  app_id: string;
  app_name: string;
  categories: { id: string; label: string; icon: string }[];
  branding: { primary_color: string; accent_color: string };
}

interface SubmitResponse {
  ticket_id: string;
  devops_work_item_id: number;
  status: string;
  message: string;
}

class AcidniSupportWidget extends HTMLElement {
  private shadow: ShadowRoot;
  private config: WidgetConfig | null = null;
  private isOpen = false;
  private apiUrl = "";
  private appId = "";
  private position = "bottom-right";

  static get observedAttributes(): string[] {
    return ["app-id", "api-url", "position"];
  }

  constructor() {
    super();
    this.shadow = this.attachShadow({ mode: "open" });
  }

  connectedCallback(): void {
    this.appId = this.getAttribute("app-id") || "";
    this.apiUrl =
      this.getAttribute("api-url") ||
      "https://apim-terprint-dev.azure-api.net/support";
    this.position = this.getAttribute("position") || "bottom-right";
    this.render();
    this.loadConfig();
  }

  attributeChangedCallback(
    name: string,
    _old: string | null,
    value: string | null
  ): void {
    if (name === "app-id") this.appId = value || "";
    if (name === "api-url") this.apiUrl = value || "";
    if (name === "position") this.position = value || "bottom-right";
  }

  private async loadConfig(): Promise<void> {
    if (!this.appId) return;
    try {
      const res = await fetch(`${this.apiUrl}/config/${this.appId}`);
      if (res.ok) {
        this.config = await res.json();
        this.renderCategories();
      }
    } catch (e) {
      console.warn("[acidni-support] Failed to load config:", e);
    }
  }

  private render(): void {
    const isInline = this.position === "inline";

    this.shadow.innerHTML = `
      <style>${WIDGET_STYLES}</style>
      ${
        isInline
          ? ""
          : `<button class="fab fab-${this.position}" id="fab" aria-label="Get Support">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
              </svg>
            </button>`
      }
      <div class="panel ${isInline ? "panel-inline" : `panel-${this.position}`}" id="panel" ${isInline ? 'style="display:block;position:relative;"' : ""}>
        <div class="panel-header">
          <span class="panel-title">Support</span>
          ${isInline ? "" : '<button class="close-btn" id="close-btn" aria-label="Close">&times;</button>'}
        </div>
        <div class="panel-body" id="panel-body">
          <div class="categories" id="categories">
            <p class="loading">Loading...</p>
          </div>
        </div>
      </div>
    `;

    // Bind events
    const fab = this.shadow.getElementById("fab");
    if (fab) fab.addEventListener("click", () => this.toggle());

    const closeBtn = this.shadow.getElementById("close-btn");
    if (closeBtn) closeBtn.addEventListener("click", () => this.close());
  }

  private renderCategories(): void {
    const container = this.shadow.getElementById("categories");
    if (!container || !this.config) return;

    const cats = this.config.categories;
    container.innerHTML = cats
      .map(
        (c) => `
      <button class="category-btn" data-id="${c.id}">
        <span class="cat-icon">${c.icon}</span>
        <span class="cat-label">${c.label}</span>
      </button>
    `
      )
      .join("");

    container.querySelectorAll(".category-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        const id = (btn as HTMLElement).dataset.id!;
        this.showForm(id);
      });
    });
  }

  private showForm(categoryId: string): void {
    const body = this.shadow.getElementById("panel-body");
    if (!body) return;

    body.innerHTML = `
      <form id="support-form" class="support-form">
        <input type="hidden" name="category" value="${categoryId}" />
        <div class="field">
          <label for="subject">Subject</label>
          <input type="text" id="subject" name="subject" required maxlength="200" placeholder="Brief summary" />
        </div>
        <div class="field">
          <label for="description">Description</label>
          <textarea id="description" name="description" required rows="4" maxlength="5000" placeholder="Tell us more..."></textarea>
        </div>
        <div class="field">
          <label for="email">Your Email (optional)</label>
          <input type="email" id="email" name="email" placeholder="you@example.com" />
        </div>
        <div class="field">
          <label for="priority">Priority</label>
          <select id="priority" name="priority">
            <option value="3">Normal</option>
            <option value="2">High</option>
            <option value="1">Critical</option>
          </select>
        </div>
        <div class="actions">
          <button type="button" class="btn-back" id="back-btn">← Back</button>
          <button type="submit" class="btn-submit">Submit</button>
        </div>
        <div id="form-status" class="form-status"></div>
      </form>
    `;

    const form = this.shadow.getElementById("support-form") as HTMLFormElement;
    form.addEventListener("submit", (e) => this.handleSubmit(e));

    const backBtn = this.shadow.getElementById("back-btn");
    if (backBtn) {
      backBtn.addEventListener("click", () => {
        body.innerHTML = '<div class="categories" id="categories"></div>';
        this.renderCategories();
      });
    }
  }

  private async handleSubmit(e: Event): Promise<void> {
    e.preventDefault();
    const form = e.target as HTMLFormElement;
    const status = this.shadow.getElementById("form-status");
    const submitBtn = form.querySelector(".btn-submit") as HTMLButtonElement;

    const data = new FormData(form);
    submitBtn.disabled = true;
    submitBtn.textContent = "Submitting...";

    const payload = {
      app_id: this.appId,
      category: data.get("category"),
      subject: data.get("subject"),
      description: data.get("description"),
      user_email: data.get("email") || undefined,
      priority: parseInt(data.get("priority") as string) || 3,
      context: {
        url: window.location.href,
        browser: navigator.userAgent,
        screen_resolution: `${window.screen.width}x${window.screen.height}`,
      },
    };

    try {
      const res = await fetch(`${this.apiUrl}/submit`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        const result: SubmitResponse = await res.json();
        this.showSuccess(result);
      } else {
        const err = await res.json().catch(() => ({}));
        if (status)
          status.innerHTML = `<p class="error">Failed: ${(err as Record<string, string>).detail || "Unknown error"}</p>`;
        submitBtn.disabled = false;
        submitBtn.textContent = "Submit";
      }
    } catch (err) {
      if (status)
        status.innerHTML = '<p class="error">Network error. Please try again.</p>';
      submitBtn.disabled = false;
      submitBtn.textContent = "Submit";
    }
  }

  private showSuccess(result: SubmitResponse): void {
    const body = this.shadow.getElementById("panel-body");
    if (!body) return;

    body.innerHTML = `
      <div class="success">
        <div class="success-icon">✅</div>
        <h3>Submitted!</h3>
        <p>${result.message}</p>
        <p class="ticket-id">Ticket: <strong>${result.ticket_id}</strong></p>
        <button class="btn-submit" id="done-btn">Done</button>
      </div>
    `;

    const doneBtn = this.shadow.getElementById("done-btn");
    if (doneBtn) {
      doneBtn.addEventListener("click", () => {
        const panelBody = this.shadow.getElementById("panel-body");
        if (panelBody) {
          panelBody.innerHTML =
            '<div class="categories" id="categories"></div>';
          this.renderCategories();
        }
        if (this.position !== "inline") this.close();
      });
    }
  }

  private toggle(): void {
    this.isOpen ? this.close() : this.open();
  }

  private open(): void {
    const panel = this.shadow.getElementById("panel");
    if (panel) panel.classList.add("open");
    this.isOpen = true;
  }

  private close(): void {
    const panel = this.shadow.getElementById("panel");
    if (panel) panel.classList.remove("open");
    this.isOpen = false;
  }
}

// Register the custom element
if (!customElements.get("acidni-support")) {
  customElements.define("acidni-support", AcidniSupportWidget);
}

export { AcidniSupportWidget };
