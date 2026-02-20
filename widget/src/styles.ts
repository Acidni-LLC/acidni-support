/**
 * Shadow DOM styles for the acidni-support widget.
 * All styles are scoped to the shadow root — no CSS leakage.
 */
export const WIDGET_STYLES = `
  :host {
    --primary: #2563eb;
    --primary-hover: #1d4ed8;
    --accent: #10b981;
    --bg: #ffffff;
    --bg-secondary: #f9fafb;
    --text: #111827;
    --text-secondary: #6b7280;
    --border: #e5e7eb;
    --radius: 12px;
    --shadow: 0 10px 25px rgba(0,0,0,0.15);
    font-family: system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
    font-size: 14px;
    color: var(--text);
  }

  /* ── Floating Action Button ─────────────────────────────────── */
  .fab {
    position: fixed;
    z-index: 99999;
    width: 56px;
    height: 56px;
    border-radius: 50%;
    background: var(--primary);
    color: white;
    border: none;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: var(--shadow);
    transition: transform 0.2s, background 0.2s;
  }
  .fab:hover { transform: scale(1.1); background: var(--primary-hover); }
  .fab-bottom-right { bottom: 24px; right: 24px; }
  .fab-bottom-left  { bottom: 24px; left: 24px; }

  /* ── Slide-out Panel ────────────────────────────────────────── */
  .panel {
    position: fixed;
    z-index: 100000;
    width: 380px;
    max-width: calc(100vw - 32px);
    max-height: 560px;
    background: var(--bg);
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    display: none;
    flex-direction: column;
    overflow: hidden;
    animation: slideIn 0.25s ease-out;
  }
  .panel.open { display: flex; }
  .panel-inline {
    position: relative !important;
    display: flex !important;
    width: 100%;
    max-width: 520px;
    max-height: none;
    margin: 0 auto;
    box-shadow: 0 1px 3px rgba(0,0,0,0.12);
  }
  .panel-bottom-right { bottom: 92px; right: 24px; }
  .panel-bottom-left  { bottom: 92px; left: 24px; }

  @keyframes slideIn {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
  }

  .panel-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 20px;
    background: var(--primary);
    color: white;
  }
  .panel-title { font-weight: 600; font-size: 16px; }
  .close-btn {
    background: none;
    border: none;
    color: white;
    font-size: 22px;
    cursor: pointer;
    padding: 0 4px;
    line-height: 1;
  }

  .panel-body {
    padding: 16px 20px;
    overflow-y: auto;
    flex: 1;
  }

  /* ── Category Buttons ───────────────────────────────────────── */
  .categories {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  .category-btn {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 14px 16px;
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 8px;
    cursor: pointer;
    font-size: 14px;
    text-align: left;
    transition: border-color 0.15s, background 0.15s;
    color: var(--text);
  }
  .category-btn:hover {
    border-color: var(--primary);
    background: white;
  }
  .cat-icon { font-size: 20px; }
  .cat-label { font-weight: 500; }

  .loading {
    text-align: center;
    color: var(--text-secondary);
    padding: 20px 0;
  }
  .error-msg {
    text-align: center;
    color: #dc2626;
    padding: 16px 0;
    font-size: 13px;
  }
  .empty-msg {
    text-align: center;
    color: var(--text-secondary);
    padding: 24px 0;
    font-size: 13px;
  }

  /* ── Context Bar (app name, user greeting) ──────────────────── */
  .context-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 14px;
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 8px;
    margin-bottom: 12px;
    font-size: 13px;
  }
  .context-app { font-weight: 500; color: var(--text); }
  .context-user { color: var(--primary); font-weight: 500; }
  .context-cat {
    color: var(--text-secondary);
    font-style: italic;
  }

  /* ── Past Requests Link ─────────────────────────────────────── */
  .past-requests-link {
    margin-top: 14px;
    padding-top: 12px;
    border-top: 1px solid var(--border);
    text-align: center;
  }
  .link-btn {
    background: none;
    border: none;
    color: var(--primary);
    cursor: pointer;
    font-size: 13px;
    font-weight: 500;
    padding: 6px 12px;
    border-radius: 6px;
    transition: background 0.15s;
  }
  .link-btn:hover { background: var(--bg-secondary); }

  /* ── Past Requests List ─────────────────────────────────────── */
  .past-requests {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }
  .section-header {
    display: flex;
    align-items: center;
    gap: 12px;
  }
  .section-title {
    font-weight: 600;
    font-size: 15px;
    color: var(--text);
  }
  .tickets-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  .ticket-row {
    padding: 10px 14px;
    border: 1px solid var(--border);
    border-radius: 8px;
    background: var(--bg-secondary);
    transition: border-color 0.15s;
  }
  .ticket-row:hover { border-color: var(--primary); }
  .ticket-main {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 4px;
  }
  .ticket-status { font-size: 14px; }
  .ticket-subject {
    font-weight: 500;
    font-size: 13px;
    color: var(--text);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .ticket-meta {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 11px;
    color: var(--text-secondary);
  }
  .ticket-id-label { font-family: monospace; }
  .ticket-priority {
    padding: 1px 6px;
    border-radius: 4px;
    font-weight: 500;
  }
  .ticket-priority.critical { background: #fef2f2; color: #dc2626; }
  .ticket-priority.high { background: #fff7ed; color: #ea580c; }
  .ticket-priority.normal { background: #f0f9ff; color: #2563eb; }
  .ticket-priority.low { background: #f9fafb; color: #6b7280; }
  .ticket-date { color: var(--text-secondary); }

  /* ── Form ───────────────────────────────────────────────────── */
  .support-form { display: flex; flex-direction: column; gap: 14px; }
  .field { display: flex; flex-direction: column; gap: 4px; }
  .field label {
    font-size: 13px;
    font-weight: 500;
    color: var(--text-secondary);
  }
  .required { color: #dc2626; }
  .field input,
  .field textarea,
  .field select {
    padding: 10px 12px;
    border: 1px solid var(--border);
    border-radius: 6px;
    font-size: 14px;
    font-family: inherit;
    background: white;
    color: var(--text);
    outline: none;
    transition: border-color 0.15s;
  }
  .field input:focus,
  .field textarea:focus,
  .field select:focus {
    border-color: var(--primary);
  }
  .field input.invalid,
  .field textarea.invalid {
    border-color: #dc2626;
  }
  .field-error {
    font-size: 12px;
    color: #dc2626;
    min-height: 16px;
  }
  .field textarea { resize: vertical; min-height: 80px; }

  .actions {
    display: flex;
    justify-content: space-between;
    gap: 10px;
    margin-top: 4px;
  }
  .btn-back {
    background: none;
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 10px 16px;
    cursor: pointer;
    font-size: 13px;
    color: var(--text-secondary);
  }
  .btn-back:hover { background: var(--bg-secondary); }
  .btn-submit {
    background: var(--primary);
    color: white;
    border: none;
    border-radius: 6px;
    padding: 10px 24px;
    cursor: pointer;
    font-size: 14px;
    font-weight: 500;
    transition: background 0.15s;
  }
  .btn-submit:hover { background: var(--primary-hover); }
  .btn-submit:disabled { opacity: 0.6; cursor: not-allowed; }

  .form-status { margin-top: 8px; }
  .error { color: #dc2626; font-size: 13px; margin: 0; }

  /* ── Success State ──────────────────────────────────────────── */
  .success { text-align: center; padding: 20px 0; }
  .success-icon { font-size: 48px; margin-bottom: 12px; }
  .success h3 { margin: 0 0 8px; font-size: 18px; color: var(--text); }
  .success p { margin: 4px 0; color: var(--text-secondary); font-size: 13px; }
  .ticket-id { margin-top: 12px !important; font-size: 14px !important; color: var(--text) !important; }
  .success .btn-submit { margin-top: 16px; }

  /* ── Responsive ─────────────────────────────────────────────── */
  @media (max-width: 440px) {
    .panel {
      width: calc(100vw - 16px);
      max-height: 80vh;
      bottom: 8px !important;
      right: 8px !important;
      left: 8px !important;
    }
    .fab { bottom: 16px; right: 16px; }
    .fab-bottom-left { left: 16px; }
  }
`;
