const LABELS = { name: "Device", mac: "MAC", ip: "IP", up: "Up", down: "Down" };
const displayValue = (client, column) => ["up", "down"].includes(column)
  ? `${client[column]} KB/s`
  : client[column];
const escapeHtml = value => String(value ?? "").replace(/[&<>"']/g, char => ({
  "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
})[char]);

class TPLinkRouterClientsCard extends HTMLElement {
  setConfig(config) {
    if (!config.entity) throw new Error("entity is required");
    this.config = config;
  }

  set hass(hass) {
    const state = hass.states[this.config.entity];
    if (!state) {
      this.innerHTML = `<ha-card><div class="missing">Entity not found: ${escapeHtml(this.config.entity)}</div></ha-card>`;
      return;
    }

    const clients = state.attributes.clients || [];
    const mode = this.config.mode || state.attributes.card_mode || "table";
    const columns = this.config.columns || state.attributes.columns || Object.keys(LABELS);
    const rows = mode === "compact"
      ? clients.map(client => `<div class="compact"><span>${escapeHtml(client.name)}</span><b>${client.down} KB/s ↓</b></div>`).join("")
      : `<table><thead><tr>${columns.map(column => `<th>${LABELS[column]}</th>`).join("")}</tr></thead><tbody>${clients.map(client =>
          `<tr>${columns.map(column => `<td>${escapeHtml(displayValue(client, column))}</td>`).join("")}</tr>`
        ).join("")}</tbody></table>`;

    this.innerHTML = `<ha-card header="${escapeHtml(this.config.title || "Router clients")}">
      <style>
        .content { padding: 0 16px 16px; overflow-x: auto; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border-bottom: 1px solid var(--divider-color); padding: 8px; text-align: left; white-space: nowrap; }
        th { color: var(--secondary-text-color); }
        .compact { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid var(--divider-color); }
        .missing { padding: 16px; }
      </style><div class="content">${rows || "No online clients"}</div>
    </ha-card>`;
  }

  getCardSize() { return 5; }
  static getStubConfig() { return { entity: "sensor.online_clients" }; }
}

if (!customElements.get("tplink-router-clients-card")) {
  customElements.define("tplink-router-clients-card", TPLinkRouterClientsCard);
}
window.customCards = window.customCards || [];
window.customCards.push({
  type: "tplink-router-clients-card",
  name: "TP-Link Router Clients",
  description: "Online TP-Link router clients sorted by download speed"
});
