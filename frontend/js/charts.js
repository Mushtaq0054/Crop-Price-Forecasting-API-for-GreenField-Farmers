/**
 * GreenField Farmers Co-op - Crop Price Forecasting Dashboard
 * Chart.js Visualization Module
 */

const ChartManager = {
  chartInstance: null,

  /**
   * Initialize or render the price forecasting trajectory chart
   */
  renderForecastChart(canvasId, cropName, predictedPrice, lowerBound, upperBound, targetDate) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    const cropMeta = CONFIG.CROPS[cropName] || CONFIG.CROPS.Wheat;
    const baseColor = cropMeta.color;

    // Build timeline labels (past 4 weeks + current + forecast target)
    const labels = ["4 Wks Ago", "3 Wks Ago", "2 Wks Ago", "Last Week", "Current Spot", `Forecast (${targetDate})`];
    
    // Recent historical trend from benchmark
    const historyData = [...cropMeta.historicalTrend];
    const trendValues = [...historyData, predictedPrice];

    // Upper and lower confidence curves
    const upperCurve = [null, null, null, null, historyData[historyData.length - 1], upperBound];
    const lowerCurve = [null, null, null, null, historyData[historyData.length - 1], lowerBound];

    if (this.chartInstance) {
      this.chartInstance.destroy();
    }

    this.chartInstance = new Chart(ctx, {
      type: "line",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Upper Confidence Bound (PKR)",
            data: upperCurve,
            borderColor: "rgba(34, 197, 94, 0.4)",
            borderDash: [5, 5],
            borderWidth: 1.5,
            pointRadius: 0,
            fill: "+1",
            backgroundColor: "rgba(46, 125, 50, 0.08)",
            tension: 0.3
          },
          {
            label: "Lower Confidence Bound (PKR)",
            data: lowerCurve,
            borderColor: "rgba(220, 38, 38, 0.4)",
            borderDash: [5, 5],
            borderWidth: 1.5,
            pointRadius: 0,
            fill: false,
            tension: 0.3
          },
          {
            label: `${cropName} Modal Price (PKR/quintal)`,
            data: trendValues,
            borderColor: baseColor,
            backgroundColor: baseColor,
            borderWidth: 3,
            pointBackgroundColor: labels.map((_, idx) => idx === labels.length - 1 ? "#1b5e20" : baseColor),
            pointBorderColor: "#ffffff",
            pointBorderWidth: 2,
            pointRadius: labels.map((_, idx) => idx === labels.length - 1 ? 7 : 4),
            pointHoverRadius: 9,
            tension: 0.25
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
          mode: "index",
          intersect: false
        },
        plugins: {
          legend: {
            position: "top",
            labels: {
              boxWidth: 12,
              font: { family: "-apple-system, sans-serif", size: 12, weight: "500" },
              color: "#475569"
            }
          },
          tooltip: {
            backgroundColor: "#0f172a",
            titleFont: { size: 13, weight: "bold" },
            bodyFont: { size: 12 },
            padding: 10,
            cornerRadius: 8,
            callbacks: {
              label: function (context) {
                if (context.parsed.y !== null) {
                  return `${context.dataset.label}: PKR ${context.parsed.y.toLocaleString(undefined, { minimumFractionDigits: 1, maximumFractionDigits: 1 })}`;
                }
                return "";
              }
            }
          }
        },
        scales: {
          x: {
            grid: { color: "rgba(226, 232, 240, 0.6)" },
            ticks: { color: "#64748b", font: { size: 11, weight: "600" } }
          },
          y: {
            grid: { color: "rgba(226, 232, 240, 0.6)" },
            ticks: {
              color: "#64748b",
              font: { size: 11 },
              callback: function (val) {
                return "PKR " + val;
              }
            }
          }
        }
      }
    });
  }
};

