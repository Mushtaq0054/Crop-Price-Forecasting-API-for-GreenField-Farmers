/**
 * GreenField Farmers Co-op - Crop Price Forecasting Dashboard
 * API Client Module
 */

const ApiClient = {
  /**
   * Check connection and health status of the API server
   */
  async checkHealth() {
    const baseUrl = CONFIG.getBaseUrl();
    const url = `${baseUrl}/health`;

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 6000);

      const response = await fetch(url, {
        method: "GET",
        signal: controller.signal,
        headers: { "Accept": "application/json" }
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`Health check returned status ${response.status}`);
      }

      const data = await response.json();
      return {
        online: true,
        healthy: data.status === "healthy",
        modelLoaded: data.model_loaded,
        supportedCrops: data.supported_crops || ["Wheat", "Rice", "Potato"],
        url: baseUrl || window.location.origin
      };
    } catch (err) {
      console.warn("[ApiClient] Health check failed:", err.message);
      return {
        online: false,
        healthy: false,
        modelLoaded: false,
        error: err.name === "AbortError" ? "Connection timed out" : err.message,
        url: baseUrl || window.location.origin
      };
    }
  },

  /**
   * Request next-week modal price forecast
   * @param {Object} payload { crop, date, current_price_pkr, market_arrival_tonnes, rainfall_mm, temperature_c }
   */
  async predictPrice(payload) {
    const baseUrl = CONFIG.getBaseUrl();
    const url = `${baseUrl}/predict`;

    try {
      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Accept": "application/json"
        },
        body: JSON.stringify(payload)
      });

      const data = await response.json();

      if (!response.ok) {
        // Parse validation errors
        let errorMsg = "Prediction request failed.";
        if (data.detail) {
          if (Array.isArray(data.detail)) {
            errorMsg = data.detail.map(d => `${d.loc ? d.loc.join('.') : ''}: ${d.msg}`).join("; ");
          } else {
            errorMsg = data.detail;
          }
        }
        throw new Error(errorMsg);
      }

      return data;
    } catch (err) {
      console.error("[ApiClient] Prediction error:", err);
      throw err;
    }
  }
};

