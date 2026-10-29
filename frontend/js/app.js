/**
 * GreenField Farmers Co-op - Crop Price Forecasting Dashboard
 * Master Application Controller
 */

document.addEventListener("DOMContentLoaded", () => {
  App.init();
});

const App = {
  selectedCrop: "Wheat",

  init() {
    this.cacheDom();
    this.bindEvents();
    this.setDefaultDate();
    this.populateBenchmarksTicker();
    this.checkConnection();
    this.renderHistoryTable();
    this.selectCrop(this.selectedCrop);
  },

  cacheDom() {
    this.dom = {
      // Server & Connection
      serverSelect: document.getElementById("serverEndpointSelect"),
      statusPill: document.getElementById("connectionStatusPill"),
      statusDot: document.getElementById("connectionStatusDot"),
      statusText: document.getElementById("connectionStatusText"),

      // Form Controls
      form: document.getElementById("forecastForm"),
      cropCards: document.querySelectorAll(".crop-card-option"),
      dateInput: document.getElementById("forecastDate"),
      quickDateChips: document.querySelectorAll(".quick-date-chip"),
      currentPriceInput: document.getElementById("currentPriceInput"),
      arrivalInput: document.getElementById("arrivalInput"),
      rainfallInput: document.getElementById("rainfallInput"),
      temperatureInput: document.getElementById("temperatureInput"),
      submitBtn: document.getElementById("submitForecastBtn"),
      btnText: document.getElementById("submitBtnText"),
      btnSpinner: document.getElementById("submitBtnSpinner"),
      accordion: document.getElementById("advancedContextAccordion"),
      accordionHeader: document.getElementById("accordionToggleHeader"),
      resetDefaultsBtn: document.getElementById("resetDefaultsBtn"),

      // Result Display
      emptyState: document.getElementById("forecastEmptyState"),
      resultSection: document.getElementById("forecastResultSection"),
      resultCropIcon: document.getElementById("resultCropIcon"),
      resultCropName: document.getElementById("resultCropName"),
      resultTargetDate: document.getElementById("resultTargetDate"),
      predictedPriceVal: document.getElementById("predictedPriceValue"),
      priceDeltaBadge: document.getElementById("priceDeltaBadge"),
      lowerBoundVal: document.getElementById("lowerBoundValue"),
      upperBoundVal: document.getElementById("upperBoundValue"),
      advisoryBox: document.getElementById("coopAdvisoryBox"),
      advisoryIcon: document.getElementById("advisoryIcon"),
      advisoryTitle: document.getElementById("advisoryTitle"),
      advisoryMsg: document.getElementById("advisoryMessage"),

      // History Table
      historyTableBody: document.getElementById("historyTableBody"),
      emptyHistoryRow: document.getElementById("emptyHistoryRow"),
      clearHistoryBtn: document.getElementById("clearHistoryBtn"),
      exportCsvBtn: document.getElementById("exportCsvBtn"),

      // Model Card Modal
      modalOverlay: document.getElementById("modelCardModal"),
      openModalBtn: document.getElementById("openModelCardBtn"),
      closeModalBtn: document.getElementById("closeModelCardBtn"),

      // Toast Container
      toastContainer: document.getElementById("toastContainer")
    };
  },

  bindEvents() {
    // Crop selection
    this.dom.cropCards.forEach(card => {
      card.addEventListener("click", () => {
        const crop = card.getAttribute("data-crop");
        this.selectCrop(crop);
      });
    });

    // Quick date selectors
    this.dom.quickDateChips.forEach(chip => {
      chip.addEventListener("click", () => {
        const days = parseInt(chip.getAttribute("data-days"), 10);
        this.setOffsetDate(days);
        this.dom.quickDateChips.forEach(c => c.classList.remove("active"));
        chip.classList.add("active");
      });
    });

    // Advanced accordion toggle
    if (this.dom.accordionHeader) {
      this.dom.accordionHeader.addEventListener("click", () => {
        this.dom.accordion.classList.toggle("open");
      });
    }

    // Reset defaults button
    if (this.dom.resetDefaultsBtn) {
      this.dom.resetDefaultsBtn.addEventListener("click", () => {
        this.loadCropDefaults(this.selectedCrop);
        this.showToast(`Applied default cooperative benchmarks for ${this.selectedCrop}.`, "info");
      });
    }

    // Form submission
    if (this.dom.form) {
      this.dom.form.addEventListener("submit", (e) => this.handleForecastSubmit(e));
    }

    // Server dropdown change
    if (this.dom.serverSelect) {
      this.dom.serverSelect.value = CONFIG.getBaseUrl() || CONFIG.SERVERS.LOCAL;
      this.dom.serverSelect.addEventListener("change", (e) => {
        CONFIG.setBaseUrl(e.target.value);
        this.checkConnection();
        this.showToast("API endpoint updated to: " + e.target.value, "info");
      });
    }

    // Model Card Modal
    if (this.dom.openModalBtn) {
      this.dom.openModalBtn.addEventListener("click", () => this.toggleModal(true));
    }
    if (this.dom.closeModalBtn) {
      this.dom.closeModalBtn.addEventListener("click", () => this.toggleModal(false));
    }
    if (this.dom.modalOverlay) {
      this.dom.modalOverlay.addEventListener("click", (e) => {
        if (e.target === this.dom.modalOverlay) this.toggleModal(false);
      });
    }

    // History actions
    if (this.dom.clearHistoryBtn) {
      this.dom.clearHistoryBtn.addEventListener("click", () => {
        if (confirm("Are you sure you want to clear your saved forecast history?")) {
          StorageManager.clearHistory();
          this.renderHistoryTable();
          this.showToast("Forecast history cleared.", "info");
        }
      });
    }

    if (this.dom.exportCsvBtn) {
      this.dom.exportCsvBtn.addEventListener("click", () => {
        StorageManager.exportToCsv();
      });
    }
  },

  selectCrop(cropName) {
    this.selectedCrop = cropName;
    this.dom.cropCards.forEach(card => {
      if (card.getAttribute("data-crop") === cropName) {
        card.classList.add("active");
        const radio = card.querySelector("input[type='radio']");
        if (radio) radio.checked = true;
      } else {
        card.classList.remove("active");
      }
    });

    this.loadCropDefaults(cropName);
  },

  loadCropDefaults(cropName) {
    const meta = CONFIG.CROPS[cropName];
    if (!meta) return;

    if (this.dom.currentPriceInput) this.dom.currentPriceInput.placeholder = `e.g. ${meta.defaultPrice} PKR (Benchmark)`;
    if (this.dom.arrivalInput) this.dom.arrivalInput.placeholder = `e.g. ${meta.defaultArrival} Tonnes`;
    if (this.dom.temperatureInput) this.dom.temperatureInput.placeholder = `e.g. ${meta.defaultTemp} °C`;
    if (this.dom.rainfallInput) this.dom.rainfallInput.placeholder = `e.g. ${meta.defaultRainfall} mm`;
  },

  setDefaultDate() {
    this.setOffsetDate(7); // Next week by default
  },

  setOffsetDate(days) {
    const d = new Date();
    d.setDate(d.getDate() + days);
    const dateStr = d.toISOString().split("T")[0];
    if (this.dom.dateInput) {
      this.dom.dateInput.value = dateStr;
    }
  },

  populateBenchmarksTicker() {
    // Populate the 3 crop benchmark cards at the top
    const container = document.getElementById("benchmarkStripContainer");
    if (!container) return;

    const cardsHtml = Object.values(CONFIG.CROPS).map(crop => `
      <div class="benchmark-card benchmark-${crop.name.toLowerCase()}">
        <div class="benchmark-icon-box">${crop.symbol}</div>
        <div class="benchmark-details">
          <div class="benchmark-name">${crop.name} (${crop.variety})</div>
          <div class="benchmark-price">PKR ${crop.defaultPrice.toLocaleString()}</div>
          <div class="benchmark-meta">Modal Benchmark • Arrival: ${crop.defaultArrival}t</div>
        </div>
      </div>
    `).join("");

    container.innerHTML = cardsHtml;
  },

  async checkConnection() {
    if (this.dom.statusDot) {
      this.dom.statusDot.className = "status-dot";
      this.dom.statusText.textContent = "Connecting...";
    }

    const health = await ApiClient.checkHealth();

    if (health.online && health.healthy) {
      this.dom.statusDot.className = "status-dot online";
      this.dom.statusText.textContent = "Live: Model v1.0 (GBR Active)";
      this.dom.statusPill.className = "badge badge-success";
    } else if (health.online) {
      this.dom.statusDot.className = "status-dot online";
      this.dom.statusText.textContent = "Degraded (Fallback Active)";
      this.dom.statusPill.className = "badge badge-warning";
    } else {
      this.dom.statusDot.className = "status-dot offline";
      this.dom.statusText.textContent = "Offline / Connection Failed";
      this.dom.statusPill.className = "badge badge-danger";
    }
  },

  async handleForecastSubmit(e) {
    e.preventDefault();

    const crop = this.selectedCrop;
    const date = this.dom.dateInput.value;

    if (!crop || !date) {
      this.showToast("Please select a crop and target date.", "error");
      return;
    }

    // Build payload
    const payload = {
      crop: crop,
      date: date
    };

    const currentPrice = parseFloat(this.dom.currentPriceInput.value);
    if (!isNaN(currentPrice) && currentPrice > 0) payload.current_price_pkr = currentPrice;

    const arrival = parseFloat(this.dom.arrivalInput.value);
    if (!isNaN(arrival) && arrival >= 0) payload.market_arrival_tonnes = arrival;

    const rainfall = parseFloat(this.dom.rainfallInput.value);
    if (!isNaN(rainfall) && rainfall >= 0) payload.rainfall_mm = rainfall;

    const temp = parseFloat(this.dom.temperatureInput.value);
    if (!isNaN(temp)) payload.temperature_c = temp;

    // UI Loading state
    this.setLoading(true);

    try {
      const response = await ApiClient.predictPrice(payload);
      this.displayPredictionResult(response, payload);
      StorageManager.savePrediction(response, payload);
      this.renderHistoryTable();
      this.showToast(`Forecast generated for ${response.crop}!`, "success");
    } catch (err) {
      this.showToast(err.message || "Could not retrieve forecast from API.", "error");
    } finally {
      this.setLoading(false);
    }
  },

  displayPredictionResult(data, reqPayload) {
    const cropMeta = CONFIG.CROPS[data.crop] || CONFIG.CROPS.Wheat;
    const predicted = data.predicted_next_week_price_pkr;
    const lower = data.confidence_interval_pkr.lower_bound;
    const upper = data.confidence_interval_pkr.upper_bound;
    const baseRef = reqPayload.current_price_pkr || cropMeta.defaultPrice;

    const diff = predicted - baseRef;
    const pctDiff = ((diff / baseRef) * 100).toFixed(1);

    // Hide empty state, reveal result
    this.dom.emptyState.style.display = "none";
    this.dom.resultSection.style.display = "block";

    // Update result card texts
    this.dom.resultCropIcon.textContent = cropMeta.symbol;
    this.dom.resultCropName.textContent = data.crop;
    this.dom.resultTargetDate.textContent = `Forecast for Week of ${data.target_date}`;
    this.dom.predictedPriceVal.textContent = predicted.toLocaleString(undefined, { minimumFractionDigits: 1, maximumFractionDigits: 1 });
    this.dom.lowerBoundVal.textContent = `PKR ${lower.toLocaleString(undefined, { minimumFractionDigits: 1, maximumFractionDigits: 1 })}`;
    this.dom.upperBoundVal.textContent = `PKR ${upper.toLocaleString(undefined, { minimumFractionDigits: 1, maximumFractionDigits: 1 })}`;

    // Delta badge
    if (diff > 0) {
      this.dom.priceDeltaBadge.className = "badge badge-success";
      this.dom.priceDeltaBadge.innerHTML = `▲ +${pctDiff}% vs Current Spot`;
    } else if (diff < 0) {
      this.dom.priceDeltaBadge.className = "badge badge-danger";
      this.dom.priceDeltaBadge.innerHTML = `▼ ${pctDiff}% vs Current Spot`;
    } else {
      this.dom.priceDeltaBadge.className = "badge badge-info";
      this.dom.priceDeltaBadge.innerHTML = `▶ Stable Price Expected`;
    }

    // Farmer Advisory
    this.renderAdvisory(data.crop, diff, pctDiff, predicted);

    // Draw Chart
    ChartManager.renderForecastChart(
      "forecastTrajectoryChart",
      data.crop,
      predicted,
      lower,
      upper,
      data.target_date
    );

    // Scroll smoothly to results on mobile
    if (window.innerWidth < 1080) {
      this.dom.resultSection.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  },

  renderAdvisory(crop, diff, pctDiff, predicted) {
    const box = this.dom.advisoryBox;
    const icon = this.dom.advisoryIcon;
    const title = this.dom.advisoryTitle;
    const msg = this.dom.advisoryMsg;

    if (diff > 35) {
      box.className = "advisory-box advisory-favorable";
      icon.textContent = "📈";
      title.textContent = "Bullish Price Outlook - Recommended Action: Stagger Sales";
      msg.textContent = `${crop} prices are projected to rise by approx. ${pctDiff}%. GreenField cooperative members are advised to hold bulk inventory for 4-6 days to capture higher wholesale auction premiums.`;
    } else if (diff < -35) {
      box.className = "advisory-box advisory-caution";
      icon.textContent = "⚠️";
      title.textContent = "Bearish Price Risk - Recommended Action: Early Release";
      msg.textContent = `${crop} prices are projected to ease downwards by approx. ${pctDiff}%, likely due to high regional arrivals. Consider scheduling mandi dispatches before next week to protect profit margins.`;
    } else {
      box.className = "advisory-box advisory-neutral";
      icon.textContent = "⚖️";
      title.textContent = "Stable Price Range - Recommended Action: Normal Scheduled Sales";
      msg.textContent = `${crop} prices are expected to hold steady within normal market volatility. Proceed with standard scheduled cooperative deliveries.`;
    }
  },

  renderHistoryTable() {
    const history = StorageManager.getRecentPredictions();
    const tbody = this.dom.historyTableBody;
    if (!tbody) return;

    if (history.length === 0) {
      tbody.innerHTML = `
        <tr id="emptyHistoryRow">
          <td colspan="6" style="text-align: center; color: var(--text-muted); padding: 24px;">
            No forecasts recorded yet. Generate your first prediction above!
          </td>
        </tr>
      `;
      return;
    }

    tbody.innerHTML = history.map(item => {
      const cropMeta = CONFIG.CROPS[item.crop] || { symbol: "🌾" };
      const formattedDate = new Date(item.timestamp).toLocaleDateString(undefined, { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });

      return `
        <tr>
          <td>
            <strong>${cropMeta.symbol} ${item.crop}</strong>
          </td>
          <td>${item.targetDate}</td>
          <td>
            <strong style="color: var(--color-primary-dark);">PKR ${item.predictedPrice.toLocaleString(undefined, { minimumFractionDigits: 1, maximumFractionDigits: 1 })}</strong>
          </td>
          <td>
            <span style="font-size: 0.8rem; color: var(--text-muted);">
              ${item.lowerBound.toFixed(0)} - ${item.upperBound.toFixed(0)}
            </span>
          </td>
          <td><span style="font-size: 0.75rem; color: var(--text-muted);">${formattedDate}</span></td>
          <td>
            <button class="btn btn-sm btn-secondary" onclick="App.deleteHistoryItem('${item.id}')" title="Delete record">✕</button>
          </td>
        </tr>
      `;
    }).join("");
  },

  deleteHistoryItem(id) {
    StorageManager.deleteRecord(id);
    this.renderHistoryTable();
    this.showToast("Record removed from history.", "info");
  },

  setLoading(isLoading) {
    if (this.dom.submitBtn) {
      this.dom.submitBtn.disabled = isLoading;
    }
    if (this.dom.btnSpinner) {
      this.dom.btnSpinner.style.display = isLoading ? "inline-block" : "none";
    }
    if (this.dom.btnText) {
      this.dom.btnText.textContent = isLoading ? "Analyzing Trends..." : "Generate Next-Week Forecast";
    }
  },

  toggleModal(isOpen) {
    if (this.dom.modalOverlay) {
      this.dom.modalOverlay.classList.toggle("active", isOpen);
    }
  },

  showToast(message, type = "info") {
    if (!this.dom.toastContainer) return;

    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
      <span>${message}</span>
      <button style="background: none; border: none; color: inherit; cursor: pointer; font-size: 16px;">✕</button>
    `;

    toast.querySelector("button").onclick = () => toast.remove();
    this.dom.toastContainer.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transition = "opacity 0.3s";
      setTimeout(() => toast.remove(), 300);
    }, 4500);
  }
};

