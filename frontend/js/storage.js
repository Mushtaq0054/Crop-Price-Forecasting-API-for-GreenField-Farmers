/**
 * GreenField Farmers Co-op - Crop Price Forecasting Dashboard
 * Local Storage & History Manager
 */

const StorageManager = {
  getRecentPredictions() {
    try {
      const data = localStorage.getItem(CONFIG.STORAGE_KEYS.RECENT_PREDICTIONS);
      return data ? JSON.parse(data) : [];
    } catch (e) {
      console.error("[Storage] Failed loading predictions history:", e);
      return [];
    }
  },

  savePrediction(prediction, requestPayload) {
    try {
      const history = this.getRecentPredictions();
      const record = {
        id: "pred_" + Date.now(),
        timestamp: new Date().toISOString(),
        crop: prediction.crop,
        targetDate: prediction.target_date,
        predictedPrice: prediction.predicted_next_week_price_pkr,
        lowerBound: prediction.confidence_interval_pkr.lower_bound,
        upperBound: prediction.confidence_interval_pkr.upper_bound,
        currency: prediction.currency || "PKR per Quintal",
        modelVersion: prediction.model_version,
        inputs: requestPayload
      };

      // Keep latest 25 predictions
      history.unshift(record);
      if (history.length > 25) {
        history.pop();
      }

      localStorage.setItem(CONFIG.STORAGE_KEYS.RECENT_PREDICTIONS, JSON.stringify(history));
      return record;
    } catch (e) {
      console.error("[Storage] Failed saving prediction:", e);
      return null;
    }
  },

  clearHistory() {
    localStorage.removeItem(CONFIG.STORAGE_KEYS.RECENT_PREDICTIONS);
  },

  deleteRecord(id) {
    const history = this.getRecentPredictions().filter(item => item.id !== id);
    localStorage.setItem(CONFIG.STORAGE_KEYS.RECENT_PREDICTIONS, JSON.stringify(history));
    return history;
  },

  /**
   * Export predictions log as CSV for farmers' records
   */
  exportToCsv() {
    const history = this.getRecentPredictions();
    if (history.length === 0) {
      alert("No predictions to export yet.");
      return;
    }

    const headers = [
      "Record ID",
      "Timestamp",
      "Crop",
      "Target Date",
      "Predicted Price (PKR/quintal)",
      "Lower Bound (PKR)",
      "Upper Bound (PKR)",
      "Current Price Input",
      "Market Arrival (Tonnes)",
      "Model Version"
    ];

    const rows = history.map(item => [
      item.id,
      item.timestamp,
      item.crop,
      item.targetDate,
      item.predictedPrice.toFixed(2),
      item.lowerBound.toFixed(2),
      item.upperBound.toFixed(2),
      item.inputs?.current_price_pkr || "Auto-Benchmark",
      item.inputs?.market_arrival_tonnes || "Auto-Benchmark",
      item.modelVersion
    ]);

    const csvContent = "data:text/csv;charset=utf-8,"
      + [headers.join(","), ...rows.map(e => e.join(","))].join("\n");

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `GreenField_Crop_Predictions_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }
};

