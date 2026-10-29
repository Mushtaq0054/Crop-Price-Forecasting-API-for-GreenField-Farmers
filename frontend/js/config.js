/**
 * GreenField Farmers Co-op - Crop Price Forecasting Dashboard
 * Configuration & Constant Benchmarks
 */

const CONFIG = {
  // Available API Servers
  SERVERS: {
    AUTO: "AUTO",
    LOCAL: "http://127.0.0.1:8000",
    RENDER: "https://crop-price-forecasting-api.onrender.com"
  },

  // Storage Keys
  STORAGE_KEYS: {
    ACTIVE_SERVER: "gff_active_server_url",
    RECENT_PREDICTIONS: "gff_recent_predictions_log",
    SELECTED_CROP: "gff_last_selected_crop"
  },

  // Cooperative Crop Reference Benchmarks
  CROPS: {
    Wheat: {
      name: "Wheat",
      symbol: "🌾",
      variety: "Shalimar / Lok-1",
      defaultPrice: 3800.0,
      defaultArrival: 410.0,
      defaultTemp: 22.0,
      defaultRainfall: 0.0,
      color: "#eab308",
      accentBg: "#fefce8",
      historicalTrend: [3650, 3680, 3720, 3760, 3800]
    },
    Rice: {
      name: "Rice",
      symbol: "🍚",
      variety: "Super Basmati",
      defaultPrice: 4350.0,
      defaultArrival: 460.0,
      defaultTemp: 24.0,
      defaultRainfall: 0.0,
      color: "#10b981",
      accentBg: "#ecfdf5",
      historicalTrend: [4150, 4200, 4250, 4300, 4350]
    },
    Potato: {
      name: "Potato",
      symbol: "🥔",
      variety: "Santa / Cardinal",
      defaultPrice: 2250.0,
      defaultArrival: 580.0,
      defaultTemp: 20.0,
      defaultRainfall: 0.0,
      color: "#b45309",
      accentBg: "#fffbeb",
      historicalTrend: [2100, 2140, 2180, 2220, 2250]
    }
  },

  // Resolve Active API Base URL
  getBaseUrl() {
    const saved = localStorage.getItem(this.STORAGE_KEYS.ACTIVE_SERVER);
    if (saved && saved !== this.SERVERS.AUTO) {
      return saved.replace(/\/+$/, "");
    }
    // If running in browser over http or https (on Render or local FastAPI server)
    if (window.location.protocol.startsWith("http")) {
      return window.location.origin;
    }
    // Default fallback when opened as local file (file:///)
    return this.SERVERS.LOCAL;
  },

  setBaseUrl(url) {
    localStorage.setItem(this.STORAGE_KEYS.ACTIVE_SERVER, url);
  }
};

