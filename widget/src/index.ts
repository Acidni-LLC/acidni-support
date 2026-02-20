/**
 * acidni-support-widget — Embeddable support web component.
 *
 * Usage:
 *   <acidni-support app-id="terprint-web" api-url="https://apim-terprint-dev.azure-api.net/support/api"></acidni-support>
 *   <script src="https://support.acidni.net/api/widget.js"></script>
 *
 * Attributes:
 *   app-id      — CMDB app identifier for routing
 *   api-url     — Base URL for the support API
 *   position    — "bottom-right" | "bottom-left" | "inline"
 *   user-email  — Pre-populate the email field
 *   user-name   — Pre-populate the name / greeting
 *
 * See docs/integration-guide.md for full integration documentation.
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

interface TicketSummary {
  ticket_id: string;
  app_id: string;
  category: string;
  subject: string;
  status: string;
  priority: number;
  created_at: string;
  devops_work_item_id: number | null;
}

class AcidniSupportWidget extends HTMLElement {
  private shadow: ShadowRoot;
  private config: WidgetConfig | null = null;
  private isOpen = false;
  private apiUrl = "";
  private appId = "";
  private position = "bottom-right";
  private userEmail = "";
  private userName = "";

  static get observedAttributes(): string[] {
    return ["app-id", "api-url", "position", "user-email", "user-name"];
  }

  constructor() {
    super();
    this.shadow = this.attachShadow({ mode: "open" });
  }

  connectedCallback(): void {
    this.appId = this.getAttribute("app-id") || "";
    this.apiUrl =
      this.getAttribute("api-url") ||
      "https://apim-terprint-dev.azure-api.net/support/api";
    this.position = this.getAttribute("position") || "bottom-right";
    this.userEmail = this.getAttribute("user-email") || "";
    this.userName = this.getAttribute("user-name") || "";
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
    if (name === "user-email") this.userEmail = value || "";
    if (name === "user-name") this.userName = value || "";
  }

  private async loadConfig(): Promise<void> {
    if (!this.appId) return;
    try {
      const res = await fetch(`${this.apiUrl}/config/${this.appId}`);
      if (res.ok) {
        this.config = await res.json();
        this.renderHome();
      } else {
        this.renderError("Could not load support configuration.");
      }
    } catch (e) {
      console.warn("[acidni-support] Failed to load config:", e);
      this.renderError("Could not connect to support service.");
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

  private renderError(message: string): void {
    const container = this.shadow.getElementById("categories");
    if (!container) return;
    container.innerHTML = `<p class="error-msg">${message}</p>`;
  }

  /** Render the home screen with app info, categories, and past requests link */
  private renderHome(): void {
    const container = this.shadow.getElementById("panel-body");
    if (!container || !this.config) return;

    const appName = this.config.app_name || this.appId;
    const greeting = this.userName ? `Hi ${this.userName}!` : "";

    const cats = this.config.categories;
    const catButtons = cats
      .map(
        (c) => `
      <button class="category-btn" data-id="${c.id}">
        <span class="cat-icon">${c.icon}</span>
        <span class="cat-label">${c.label}</span>
      </button>
    `
      )
      .join("");

    container.innerHTML = `
      <div class="home-view">
        <div class="context-bar">
          <span class="context-app">📱 ${appName}</span>
          ${greeting ? `<span class="context-user">${greeting}</span>` : ""}
        </div>
        <div class="categories" id="categories">
          ${catButtons}
        </div>
        <div class="past-requests-link">
          <button class="link-btn" id="view-requests-btn">📋 View my past requests</button>
        </div>
      </div>
    `;

    container.querySelectorAll(".category-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        const id = (btn as HTMLElement).dataset.id!;
        this.showForm(id);
      });
    });

    const viewBtn = this.shadow.getElementById("view-requests-btn");
    if (viewBtn) viewBtn.addEventListener("click", () => this.showPastRequests());
  }

  private showForm(categoryId: string): void {
    const body = this.shadow.getElementById("panel-body");
    if (!body) return;

    const catLabel =
      this.config?.categories.find((c) => c.id === categoryId)?.label || categoryId;

    body.innerHTML = `
      <form id="support-form" class="support-form" novalidate>
        <input type="hidden" name="category" value="${categoryId}" />

        <div class="context-bar">
          <span class="context-app">📱 ${this.config?.app_name || this.appId}</span>
          <span class="context-cat">${catLabel}</span>
        </div>

        <div class="field">
          <label for="subject">Subject <span class="required">*</span></label>
          <input type="text" id="subject" name="subject" required minlength="5" maxlength="200" placeholder="Brief summary of your issue" />
          <span class="field-error" id="subject-error"></span>
        </div>
        <div class="field">
          <label for="description">Description <span class="required">*</span></label>
          <textarea id="description" name="description" required minlength="10" rows="4" maxlength="5000" placeholder="Please describe in detail..."></textarea>
          <span class="field-error" id="description-error"></span>
        </div>
        <div class="field">
          <label for="email">Your Email <span class="required">*</span></label>
          <input type="email" id="email" name="email" required placeholder="you@example.com" value="${this.escapeAttr(this.userEmail)}" />
          <span class="field-error" id="email-error"></span>
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
      backBtn.addEventListener("click", () => this.renderHome());
    }
  }

  /** Client-side validation before submit */
  private validateForm(form: HTMLFormElement): boolean {
    let valid = true;

    const subject = form.querySelector("#subject") as HTMLInputElement;
    const description = form.querySelector("#description") as HTMLTextAreaElement;
    const email = form.querySelector("#email") as HTMLInputElement;

    const subjectErr = this.shadow.getElementById("subject-error");
    const descErr = this.shadow.getElementById("description-error");
    const emailErr = this.shadow.getElementById("email-error");

    // Reset
    [subjectErr, descErr, emailErr].forEach((el) => {
      if (el) el.textContent = "";
    });
    [subject, description, email].forEach((el) => el?.classList.remove("invalid"));

    if (!subject.value.trim() || subject.value.trim().length < 5) {
      if (subjectErr) subjectErr.textContent = "Subject must be at least 5 characters.";
      subject.classList.add("invalid");
      valid = false;
    }

    if (!description.value.trim() || description.value.trim().length < 10) {
      if (descErr) descErr.textContent = "Description must be at least 10 characters.";
      description.classList.add("invalid");
      valid = false;
    }

    if (!email.value.trim()) {
      if (emailErr) emailErr.textContent = "Email is required so we can follow up.";
      email.classList.add("invalid");
      valid = false;
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value.trim())) {
      if (emailErr) emailErr.textContent = "Please enter a valid email address.";
      email.classList.add("invalid");
      valid = false;
    }

    return valid;
  }

  private async handleSubmit(e: Event): Promise<void> {
    e.preventDefault();
    const form = e.target as HTMLFormElement;
    const status = this.shadow.getElementById("form-status");
    const submitBtn = form.querySelector(".btn-submit") as HTMLButtonElement;

    // Client-side validation
    if (!this.validateForm(form)) return;

    const data = new FormData(form);
    submitBtn.disabled = true;
    submitBtn.textContent = "Submitting...";

    const payload = {
      app_id: this.appId,
      category: data.get("category"),
      subject: data.get("subject"),
      description: data.get("description"),
      user_email: data.get("email") || undefined,
      user_name: this.userName || undefined,
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
        const err = await res.json().catch(() => ({ detail: "Unknown error" }));
        const message = this.formatErrorDetail(err.detail);
        if (status) status.innerHTML = `<p class="error">${message}</p>`;
        submitBtn.disabled = false;
        submitBtn.textContent = "Submit";
      }
    } catch (err) {
      if (status)
        status.innerHTML =
          '<p class="error">Network error. Please try again.</p>';
      submitBtn.disabled = false;
      submitBtn.textContent = "Submit";
    }
  }

  /** Format FastAPI validation error details into human-readable text */
  private formatErrorDetail(detail: unknown): string {
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail)) {
      // Pydantic validation errors: [{loc: [...], msg: "...", type: "..."}]
      return detail
        .map((d: { loc?: string[]; msg?: string }) => {
          const field = d.loc ? d.loc[d.loc.length - 1] : "field";
          return `${field}: ${d.msg || "invalid"}`;
        })
        .join("; ");
    }
    if (detail && typeof detail === "object") {
      return (detail as { message?: string }).message || JSON.stringify(detail);
    }
    return "An unexpected error occurred.";
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
        this.renderHome();
        if (this.position !== "inline") this.close();
      });
    }
  }

  /** Show a list of the user's past support tickets */
  private async showPastRequests(): Promise<void> {
    const body = this.shadow.getElementById("panel-body");
    if (!body) return;

    body.innerHTML = `
      <div class="past-requests">
        <div class="section-header">
          <button class="btn-back" id="back-btn">← Back</button>
          <span class="section-title">My Requests</span>
        </div>
        <div id="tickets-list" class="tickets-list">
          <p class="loading">Loading requests...</p>
        </div>
      </div>
    `;

    const backBtn = this.shadow.getElementById("back-btn");
    if (backBtn) backBtn.addEventListener("click", () => this.renderHome());

    // Fetch tickets
    try {
      const params = new URLSearchParams();
      if (this.appId) params.set("app_id", this.appId);
      if (this.userEmail) params.set("email", this.userEmail);
      params.set("limit", "25");

      const res = await fetch(`${this.apiUrl}/tickets?${params.toString()}`);
      const tickets: TicketSummary[] = res.ok ? await res.json() : [];
      this.renderTicketList(tickets);
    } catch (e) {
      const list = this.shadow.getElementById("tickets-list");
      if (list) list.innerHTML = '<p class="error-msg">Could not load tickets.</p>';
    }
  }

  private renderTicketList(tickets: TicketSummary[]): void {
    const list = this.shadow.getElementById("tickets-list");
    if (!list) return;

    if (tickets.length === 0) {
      list.innerHTML = '<p class="empty-msg">No past requests found.</p>';
      return;
    }

    const statusIcons: Record<string, string> = {
      created: "🟡",
      "in-progress": "🔵",
      resolved: "🟢",
      closed: "⚫",
    };

    const priorityLabels: Record<number, string> = {
      1: "Critical",
      2: "High",
      3: "Normal",
      4: "Low",
    };

    list.innerHTML = tickets
      .map((t) => {
        const icon = statusIcons[t.status] || "⚪";
        const date = t.created_at
          ? new Date(t.created_at).toLocaleDateString()
          : "";
        const pri = priorityLabels[t.priority] || "";
        return `
          <div class="ticket-row">
            <div class="ticket-main">
              <span class="ticket-status">${icon}</span>
              <span class="ticket-subject">${this.escapeHtml(t.subject)}</span>
            </div>
            <div class="ticket-meta">
              <span class="ticket-id-label">${t.ticket_id}</span>
              <span class="ticket-priority ${pri.toLowerCase()}">${pri}</span>
              <span class="ticket-date">${date}</span>
            </div>
          </div>
        `;
      })
      .join("");
  }

  private escapeHtml(str: string): string {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
  }

  private escapeAttr(str: string): string {
    return str.replace(/"/g, "&quot;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
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
