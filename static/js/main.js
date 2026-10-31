// Main JavaScript for AeroCast LSTM Web Application

// Utility to format numbers with thousand separators
function formatNumber(num) {
  return Number(num).toLocaleString('id-ID', { maximumFractionDigits: 1 });
}

// 1. Dashboard Overview Chart
function initDashboardChart() {
  const ctx = document.getElementById('dashboardChart');
  if (!ctx) return;

  fetch('/api/historical')
    .then(res => res.json())
    .then(data => {
      new Chart(ctx, {
        type: 'line',
        data: {
          labels: data.labels,
          datasets: [{
            label: 'Jumlah Penumpang (Ribuan)',
            data: data.values,
            borderColor: '#2563eb',
            backgroundColor: 'rgba(37, 99, 235, 0.08)',
            borderWidth: 2.2,
            pointRadius: 1.5,
            pointHoverRadius: 5,
            fill: true,
            tension: 0.3
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: false
            },
            tooltip: {
              backgroundColor: '#0f172a',
              titleFont: { size: 13, weight: '600' },
              bodyFont: { size: 13 },
              padding: 12,
              callbacks: {
                label: function(context) {
                  return ` Penumpang: ${context.parsed.y} ribu orang`;
                }
              }
            }
          },
          scales: {
            x: {
              grid: { display: false },
              ticks: { maxTicksLimit: 12, color: '#64748b' }
            },
            y: {
              grid: { color: '#f1f5f9' },
              ticks: { color: '#64748b' }
            }
          }
        }
      });
    })
    .catch(err => console.error('Failed to load historical chart:', err));
}

// 2. Evaluation Chart (Actual vs Predicted)
function initEvaluationChart() {
  const ctx = document.getElementById('evaluationChart');
  if (!ctx) return;

  fetch('/api/evaluation-data')
    .then(res => res.json())
    .then(data => {
      new Chart(ctx, {
        type: 'line',
        data: {
          labels: data.labels,
          datasets: [
            {
              label: 'Aktual (Ground Truth)',
              data: data.actual,
              borderColor: '#0f172a',
              backgroundColor: '#0f172a',
              borderWidth: 2.4,
              pointRadius: 4,
              pointHoverRadius: 6,
              tension: 0.2
            },
            {
              label: 'Prediksi LSTM',
              data: data.predicted,
              borderColor: '#ef4444',
              backgroundColor: '#ef4444',
              borderWidth: 2.2,
              borderDash: [5, 4],
              pointRadius: 4,
              pointStyle: 'rectRot',
              pointHoverRadius: 6,
              tension: 0.2
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'top',
              labels: {
                usePointStyle: true,
                padding: 18,
                font: { size: 13, weight: '500' }
              }
            },
            tooltip: {
              backgroundColor: '#0f172a',
              padding: 12,
              callbacks: {
                label: function(context) {
                  return ` ${context.dataset.label}: ${context.parsed.y} ribu`;
                }
              }
            }
          },
          scales: {
            x: {
              grid: { display: false },
              ticks: { color: '#64748b' }
            },
            y: {
              grid: { color: '#f1f5f9' },
              ticks: { color: '#64748b' }
            }
          }
        }
      });
    })
    .catch(err => console.error('Failed to load evaluation chart:', err));
}

// 3. Interactive Forecast Simulator
let forecastChartInstance = null;

function runForecastSimulation() {
  const horizonInput = document.getElementById('forecastHorizon');
  const scenarioInput = document.getElementById('forecastScenario');
  const customSeqInput = document.getElementById('customSequence');
  
  const horizon = horizonInput ? parseInt(horizonInput.value) : 12;
  const scenario = scenarioInput ? scenarioInput.value : 'standard';
  
  let sequence = null;
  if (customSeqInput && customSeqInput.value.trim().length > 0) {
    const rawParts = customSeqInput.value.split(',').map(x => parseFloat(x.trim())).filter(x => !isNaN(x));
    if (rawParts.length === 12) {
      sequence = rawParts;
    }
  }

  const payload = { horizon, scenario };
  if (sequence) {
    payload.sequence = sequence;
  }

  // Show loading spinner/status
  const btn = document.getElementById('btnRunForecast');
  if (btn) {
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Menghitung...';
    btn.disabled = true;
  }

  fetch('/api/forecast', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
    .then(res => res.json())
    .then(data => {
      updateForecastDisplay(data);
    })
    .catch(err => {
      console.error('Forecast failed:', err);
      alert('Terjadi kesalahan saat memproses peramalan.');
    })
    .finally(() => {
      if (btn) {
        btn.innerHTML = '<i class="fa-solid fa-wand-magic-sparkles"></i> Jalankan Simulasi Peramalan';
        btn.disabled = false;
      }
    });
}

function updateForecastDisplay(data) {
  const ctx = document.getElementById('forecastChart');
  if (!ctx) return;

  const historyLabels = data.recent_history.labels;
  const historyValues = data.recent_history.values;
  
  const forecastDates = data.forecast.map(item => item.date);
  const forecastValues = data.forecast.map(item => item.forecast);
  const lowerBounds = data.forecast.map(item => item.lower_bound);
  const upperBounds = data.forecast.map(item => item.upper_bound);

  // Combine timeline: History (12 points) + Forecast (horizon points)
  const combinedLabels = [...historyLabels, ...forecastDates];
  
  // History series (null for forecast period)
  const seriesHistory = [...historyValues, ...forecastDates.map(() => null)];
  
  // Connect history to forecast at the boundary point
  const lastHistoryVal = historyValues[historyValues.length - 1];
  const seriesForecast = [
    ...historyLabels.slice(0, -1).map(() => null),
    lastHistoryVal,
    ...forecastValues
  ];

  const seriesUpper = [
    ...historyLabels.slice(0, -1).map(() => null),
    lastHistoryVal,
    ...upperBounds
  ];

  const seriesLower = [
    ...historyLabels.slice(0, -1).map(() => null),
    lastHistoryVal,
    ...lowerBounds
  ];

  if (forecastChartInstance) {
    forecastChartInstance.destroy();
  }

  forecastChartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: combinedLabels,
      datasets: [
        {
          label: 'Data Historis (12 Bulan Terakhir)',
          data: seriesHistory,
          borderColor: '#475569',
          backgroundColor: '#475569',
          borderWidth: 2.2,
          pointRadius: 3,
          tension: 0.2
        },
        {
          label: 'Proyeksi LSTM',
          data: seriesForecast,
          borderColor: '#2563eb',
          backgroundColor: 'rgba(37, 99, 235, 0.1)',
          borderWidth: 2.5,
          pointRadius: 4,
          pointHoverRadius: 6,
          tension: 0.2
        },
        {
          label: 'Batas Atas (Upper Bound)',
          data: seriesUpper,
          borderColor: 'rgba(16, 185, 129, 0.5)',
          borderWidth: 1.5,
          borderDash: [4, 4],
          pointRadius: 0,
          fill: false,
          tension: 0.2
        },
        {
          label: 'Batas Bawah (Lower Bound)',
          data: seriesLower,
          borderColor: 'rgba(239, 68, 68, 0.5)',
          borderWidth: 1.5,
          borderDash: [4, 4],
          pointRadius: 0,
          fill: '-1', // fill to upper bound
          backgroundColor: 'rgba(37, 99, 235, 0.05)',
          tension: 0.2
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
          labels: {
            usePointStyle: true,
            filter: function(item) {
              return item.text !== 'Batas Bawah (Lower Bound)';
            }
          }
        },
        tooltip: {
          backgroundColor: '#0f172a',
          padding: 12
        }
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: { color: '#64748b' }
        },
        y: {
          grid: { color: '#f1f5f9' },
          ticks: { color: '#64748b' }
        }
      }
    }
  });

  // Populate Table
  const tableBody = document.getElementById('forecastTableBody');
  if (tableBody) {
    let rowsHtml = '';
    data.forecast.forEach(item => {
      rowsHtml += `
        <tr>
          <td><span class="badge bg-light text-dark border">Bulan +${item.step}</span></td>
          <td class="fw-bold">${item.date}</td>
          <td><span class="badge bg-primary fs-6 px-3 py-2">${formatNumber(item.forecast)}</span></td>
          <td class="text-muted">${formatNumber(item.lower_bound)}</td>
          <td class="text-muted">${formatNumber(item.upper_bound)}</td>
          <td><span class="badge bg-success-subtle text-success">Tinggi</span></td>
        </tr>
      `;
    });
    tableBody.innerHTML = rowsHtml;
  }
}

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', function() {
  initDashboardChart();
  initEvaluationChart();
  
  const btnRun = document.getElementById('btnRunForecast');
  if (btnRun) {
    btnRun.addEventListener('click', runForecastSimulation);
    // Auto run first forecast simulation
    runForecastSimulation();
  }
});
