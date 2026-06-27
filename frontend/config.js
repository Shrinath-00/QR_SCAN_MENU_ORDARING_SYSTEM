// Dynamic API & WebSocket host configuration
const isDevServer = window.location.port && window.location.port !== "8001";
const API_BASE = isDevServer ? "http://localhost:8001" : window.location.origin;
const WS_BASE = API_BASE.replace(/^http/, "ws");

const CONFIG = {
  API_URL: API_BASE,
  WS_URL: WS_BASE,
  FRONTEND_URL: window.location.origin,
  cafe: null,
  
  async loadCafeConfig() {
    if (CONFIG.cafe) return CONFIG.cafe;
    try {
      const res = await fetch(CONFIG.API_URL + "/api/cafe-config", {
        headers: { "ngrok-skip-browser-warning": "true" }
      });
      if (res.ok) {
        const data = await res.json();
        CONFIG.cafe = data;
        
        document.querySelectorAll(".cafe-name").forEach(el => {
          el.textContent = data.cafe_name;
        });
        document.querySelectorAll(".cafe-address").forEach(el => {
          el.textContent = data.cafe_address;
        });
        document.querySelectorAll(".cafe-phone").forEach(el => {
          el.textContent = data.cafe_phone;
        });
        document.querySelectorAll(".cafe-gstin").forEach(el => {
          el.textContent = data.cafe_gstin;
        });
        document.querySelectorAll(".currency-symbol").forEach(el => {
          el.textContent = data.currency_symbol;
        });
        
        if (document.title.includes("Aero Cafe")) {
          document.title = document.title.replace(/Aero Cafe/g, data.cafe_name);
        } else if (document.title.includes("AERO CAFE")) {
          document.title = document.title.replace(/AERO CAFE/g, data.cafe_name.toUpperCase());
        }
        return data;
      }
    } catch (err) {
      console.error("Failed to load cafe config:", err);
    }
    return null;
  }
};
