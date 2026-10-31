# ✈️ AeroCast LSTM: International Airline Passenger Demand Forecasting

[![Python Version](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.16-FF6F00?logo=tensorflow&logoColor=white)](https://tensorflow.org/)
[![Keras](https://img.shields.io/badge/Keras-3.14-D00000?logo=keras&logoColor=white)](https://keras.io/)
[![Flask](https://img.shields.io/badge/Flask-3.0-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.5-F7931E?logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A comprehensive, end-to-end Deep Learning system for time series sequential forecasting built with **TensorFlow / Keras LSTM** and deployed as a modern interactive **Flask Web Application**.

---

## 📌 Ringkasan Proyek (Executive Summary)

* **Mata Kuliah / Tugas**: Tugas TA04 - Machine Learning (Sequential Data & Deep Learning)
* **Domain Permasalahan**: Transportasi Udara (Aviation Capacity Planning & Demand Forecasting)
* **Dataset**: *AirPassengers Time Series* (144 observasi bulanan, 1949 – 1960)
* **Tujuan**: Memprediksi volume penumpang maskapai penerbangan internasional di masa depan berdasarkan tren jangka panjang dan pola musiman tahunan (annual seasonality).
* **Hasil Akhir**: Model LSTM terlatih, Scaler artefak, Notebook analisis tereksekusi, Aplikasi Web Flask interaktif, Dokumen Laporan Ilmiah (DOCX & PDF), dan Naskah Video Presentasi.

---

## 🏆 Kinerja Model pada Data Uji (Test Set Out-of-Sample)

Evaluasi kuantitatif dilakukan pada 20% data pengujian (27 observasi, 1958 - 1960):

| Metrik Evaluasi | Data Latih (Train Fit) | Data Uji (Test Forecast) | Interpretasi Akademik |
| :--- | :---: | :---: | :--- |
| **RMSE (Root Mean Squared Error)** | **28.648** | **34.835** | Deviasi kesalahan kuadrat sangat rendah (satuan ribuan) |
| **MAE (Mean Absolute Error)** | **23.346** | **28.141** | Rata-rata selisih absolut sangat minim |
| **MAPE (Mean Absolute % Error)** | **9.855%** | **6.592%** | **Sangat Akurat** (Kriteria Lewis: < 10%) |
| **$R^2$ Score (Koefisien Determinasi)** | **0.9000** | **0.8090** | Model mampu menjelaskan **80.9% variansi** data uji |

---

## 🧠 Arsitektur Model Deep Learning (Stacked LSTM)

Model dibangun dengan arsitektur **Sequential** berlapis:
```
[Input Tensor: (Batch, 12, 1)]
               │
               ▼
   [LSTM Layer 1: 64 Units, tanh, return_sequences=True]
               │
               ▼
   [Dropout Layer: Rate 0.20]
               │
               ▼
   [LSTM Layer 2: 32 Units, tanh, return_sequences=False]
               │
               ▼
   [Dropout Layer: Rate 0.20]
               │
               ▼
   [Dense Hidden Layer: 16 Units, ReLU]
               │
               ▼
   [Dense Output Layer: 1 Unit, Linear]
```

* **Optimizer**: Adam (Learning Rate initial: 0.001)
* **Loss Function**: Mean Squared Error (MSE)
* **Window Size (Look-back Timestep)**: 12 Bulan (merefleksikan satu siklus musiman tahunan)
* **Regulasi & Callbacks**:
  * `EarlyStopping` (patience=30, restore_best_weights=True)
  * `ReduceLROnPlateau` (factor=0.5, patience=15)

---

## 🌐 Fitur Aplikasi Web Flask

1. **Dashboard Eksekutif**: Ringkasan KPI performa, nilai ekstrem historis, dan grafik tren pertumbuhan.
2. **Eksplorasi Data (EDA)**: Grafik dekomposisi deret waktu (Trend, Seasonal, Residual) dan distribusi boxplot musiman bulanan.
3. **Evaluasi Kinerja Model**: Scorecard metrik akurasi, perbandingan data uji aktual vs prediksi, kurva loss training, dan analisis residual.
4. **Simulasi Peramalan Interaktif**:
   * Pilihan horizon masa depan (6, 12, 24, atau 36 bulan ke depan).
   * Pilihan skenario pertumbuhan pasar (Standar, Optimis +8%, Konservatif -8%).
   * Dukungan kustomisasi 12 nilai input manual.
   * Grafik Chart.js dinamis dengan pita batas toleransi kesalahan ($\pm 1$ RMSE).
   * Tabel rincian proyeksi bulanan.
5. **REST API Endpoint**:
   * `GET /api/historical` : Mengambil seluruh data deret waktu historis.
   * `GET /api/evaluation-data` : Mengambil data evaluasi aktual vs prediksi.
   * `POST /api/forecast` : Endpoint peramalan real-time untuk integrasi sistem lain.

---

## 📁 Struktur Repositori

```
tugas TA04-ML/
├── app.py                                   # Aplikasi Web Utama Flask
├── AirPassengers.csv                        # Dataset Historis Bulanan
├── train_model.py                           # Skrip Pelatihan Model & Export Artefak
├── notebook.ipynb                           # Jupyter Notebook Eksperimen Lengkap
├── requirements.txt                         # Dependensi Pustaka Python
├── Procfile                                 # Konfigurasi Gunicorn untuk Cloud Deploy
├── render.yaml                              # Konfigurasi Deploy 1-Click Render
├── Dockerfile                               # Kontainerisasi Docker
├── check_word.ps1                           # Helper skrip Office COM
├── convert_to_pdf.ps1                       # Helper konversi PDF
├── VIDEO_PRESENTATION_SCRIPT.md             # Panduan & Naskah Presentasi YouTube (5-7 Menit)
├── model/
│   ├── lstm_model.keras                     # Model Keras Format Asli
│   ├── lstm_model.h5                        # Model HDF5 Legacy
│   ├── scaler.joblib                        # Objek MinMaxScaler Terlatih
│   ├── metrics.json                         # Metrik Kuantitatif Evaluasi
│   ├── processed_passengers.csv             # Data Olahan
│   └── test_results.csv                     # Hasil Prediksi Data Uji
├── static/
│   ├── css/style.css                        # Styling Kustom SaaS/Glassmorphism
│   ├── js/main.js                           # Chart.js & Logika Interaktif AJAX
│   └── images/                              # Plot Resolusi Tinggi (300 DPI)
├── templates/
│   ├── base.html                            # Template Induk Bootstrap 5
│   ├── index.html                           # Beranda / Dashboard
│   ├── explore.html                         # Eksplorasi Data (EDA)
│   ├── evaluation.html                      # Evaluasi Model & Residual
│   ├── forecast.html                        # Simulator Peramalan Interaktif
│   └── about.html                           # Teori & Dokumentasi
└── reports/
    ├── figures/                             # Salinan Gambar untuk Laporan
    ├── Laporan_Tugas_TA04_LSTM_Time_Series.docx  # Laporan Lengkap Format DOCX
    └── Laporan_Tugas_TA04_LSTM_Time_Series.pdf   # Laporan Lengkap Format PDF
```

---

## 🚀 Panduan Menjalankan Secara Lokal

### 1. Kloning Repositori & Masuk ke Direktori
```bash
git clone https://github.com/[username]/aerocast-lstm-forecasting.git
cd aerocast-lstm-forecasting
```

### 2. Buat dan Aktifkan Virtual Environment (Disarankan)
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

### 3. Instal Dependensi
```bash
pip install -r requirements.txt
```

### 4. (Opsional) Latih Ulang Model
Jika ingin melatih ulang arsitektur LSTM dari awal:
```bash
python train_model.py
```

### 5. Jalankan Aplikasi Web Flask
```bash
python app.py
```
Buka browser dan akses alamat: **`http://localhost:5000`**

---

## ☁️ Panduan Deployment Cloud (Render / Railway)

### A. Deploy ke Render (Gratis & Cepat)
1. Fork atau Push repositori ini ke akun GitHub Anda.
2. Buka [render.com](https://render.com) dan buat **New Web Service**.
3. Hubungkan repositori GitHub Anda.
4. Konfigurasi Service:
   * **Environment**: `Python 3`
   * **Build Command**: `pip install -r requirements.txt`
   * **Start Command**: `gunicorn app:app`
5. Klik **Deploy Web Service**.

### B. Deploy menggunakan Docker
```bash
docker build -t aerocast-lstm .
docker run -p 5000:5000 aerocast-lstm
```

---

## 📡 Dokumentasi REST API

### **POST `/api/forecast`**
Melakukan peramalan autoregresif multi-step.

* **Request Headers**: `Content-Type: application/json`
* **Request Body**:
```json
{
  "horizon": 12,
  "scenario": "standard",
  "sequence": [417, 391, 419, 461, 472, 535, 622, 606, 508, 461, 390, 432]
}
```
* **Sample Response (200 OK)**:
```json
{
  "status": "success",
  "horizon": 12,
  "scenario": "standard",
  "forecast": [
    {
      "step": 1,
      "date": "1961-01",
      "forecast": 421.0,
      "lower_bound": 386.1,
      "upper_bound": 455.8
    },
    ...
  ]
}
```

---

## 📄 Berkas Laporan & Video Presentasi

* **Dokumentasi Laporan**:
  * [Laporan Tugas DOCX](reports/Laporan_Tugas_TA04_LSTM_Time_Series.docx)
  * [Laporan Tugas PDF](reports/Laporan_Tugas_TA04_LSTM_Time_Series.pdf)
* **Naskah & Panduan Video Presentasi**:
  * [VIDEO_PRESENTATION_SCRIPT.md](VIDEO_PRESENTATION_SCRIPT.md) (Naskah lengkap 5-7 menit dengan timestamped cue)

---

## 👨‍💻 Kontributor
* **Praktikan Machine Learning** - *Proyek Tugas TA04 Deep Learning & Sequential Time Series Forecasting*

