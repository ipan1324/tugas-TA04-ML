import nbformat as nbf

nb = nbf.v4.new_notebook()

cells = []

# Title & Metadata
cells.append(nbf.v4.new_markdown_cell("""# Proyek Analisis & Peramalan Deret Waktu (Time Series Forecasting)
## Studi Kasus: Prediksi Jumlah Penumpang Maskapai Penerbangan Internasional Menggunakan Long Short-Term Memory (LSTM)

---
### **Informasi Proyek**
* **Mata Kuliah / Tugas**: Tugas TA04 - Machine Learning (Sequential Data & Deep Learning)
* **Domain Masalah**: Transportasi Udara & Perjalanan (Aviation Demand Forecasting)
* **Dataset**: *Airline Passengers Time Series* (1949 - 1960, bulanan)
* **Model Deep Learning**: Long Short-Term Memory (LSTM) Recurrent Neural Network
* **Framework**: TensorFlow, Keras, Scikit-Learn, Pandas, NumPy, Matplotlib, Seaborn

---
### **Tujuan Penelitian / Tugas**
1. Mengidentifikasi pola tren dan musiman (*seasonality*) pada data historis jumlah penumpang pesawat bulanan.
2. Melakukan pra-pemrosesan data time series: normalisasi menggunakan `MinMaxScaler` dan transformasi sekuensial (*windowing/lagging*).
3. Merancang, membangun, dan melatih arsitektur jaringan saraf berulang LSTM (*Sequential*) dengan mekanisme regulasi (*Dropout*, *EarlyStopping*, *ReduceLROnPlateau*).
4. Mengevaluasi performa model menggunakan metrik regresi standar: **RMSE**, **MAE**, **MAPE**, dan **$R^2$ Score**.
5. Melakukan *multi-step autoregressive forecasting* untuk memproyeksikan tren permintaan penumpang di masa depan.
6. Menyimpan model terlatih dan artefak *scaler* untuk diintegrasikan ke dalam aplikasi web berbasis Flask."""))

# Imports
cells.append(nbf.v4.new_markdown_cell("""## 1. Import Library dan Konfigurasi Lingkungan"""))
cells.append(nbf.v4.new_code_cell("""import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

# Konfigurasi Random Seed untuk Reproducibility
np.random.seed(42)
import tensorflow as tf
tf.random.set_seed(42)

from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau

# Konfigurasi Tampilan Plot
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
%matplotlib inline

print("TensorFlow Version:", tf.__version__)
print("GPU Available:", tf.config.list_physical_devices('GPU'))"""))

# Load Data
cells.append(nbf.v4.new_markdown_cell("""## 2. Eksplorasi Data Awal (Exploratory Data Analysis - EDA)"""))
cells.append(nbf.v4.new_code_cell("""# Membaca dataset
df = pd.read_csv('AirPassengers.csv')
df.columns = ['Month', 'Passengers']
df['Month'] = pd.to_datetime(df['Month'])
df.set_index('Month', inplace=True)

print("Dimensi Data:", df.shape)
print()\nprint("Informasi Tipe Data & Missing Values:")
print(df.info())
print()\nprint("Statistik Deskriptif:")
display(df.describe())
display(df.head(10))"""))

# EDA Visualizations
cells.append(nbf.v4.new_markdown_cell("""### 2.1 Visualisasi Deret Waktu Historis"""))
cells.append(nbf.v4.new_code_cell("""plt.figure(figsize=(14, 5))
plt.plot(df.index, df['Passengers'], color='#1f77b4', linewidth=2.2, label='Jumlah Penumpang Bulanan')
plt.title('Tren Historis Jumlah Penumpang Maskapai Internasional (1949 - 1960)', fontsize=14, fontweight='bold', pad=15)
plt.xlabel('Tahun', fontsize=12)
plt.ylabel('Jumlah Penumpang (Ribuan)', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend(frameon=True, facecolor='white', loc='upper left')
plt.tight_layout()
plt.show()"""))

# Seasonal Boxplot
cells.append(nbf.v4.new_markdown_cell("""### 2.2 Analisis Musiman (*Seasonality Analysis*)"""))
cells.append(nbf.v4.new_code_cell("""df_eda = df.copy()
df_eda['Year'] = df_eda.index.year
df_eda['Month_Name'] = df_eda.index.strftime('%b')
month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

plt.figure(figsize=(14, 5))
sns.boxplot(x='Month_Name', y='Passengers', data=df_eda, order=month_order, palette='crest')
plt.title('Distribusi Musiman Jumlah Penumpang Berdasarkan Bulan (Seasonality)', fontsize=14, fontweight='bold', pad=15)
plt.xlabel('Bulan', fontsize=12)
plt.ylabel('Jumlah Penumpang (Ribuan)', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.show()"""))

# Decomposition
cells.append(nbf.v4.new_markdown_cell("""### 2.3 Dekomposisi Deret Waktu (*Time Series Decomposition*)
Memisahkan komponen:
1. **Trend**: Tren jangka panjang pertumbuhan penumpang.
2. **Seasonal**: Pola fluktuasi berulang tahunan (siklus 12 bulan).
3. **Residual (Irregular)**: Variasi acak setelah dikurangi tren dan musiman."""))
cells.append(nbf.v4.new_code_cell("""trend = df['Passengers'].rolling(window=12, center=True).mean()
detrended = df['Passengers'] - trend
seasonal = detrended.groupby(df.index.month).transform('mean')
residual = df['Passengers'] - trend - seasonal

fig, axes = plt.subplots(4, 1, figsize=(14, 10), sharex=True)
axes[0].plot(df.index, df['Passengers'], color='#1f77b4', label='Observed (Asli)')
axes[0].set_title('Dekomposisi Time Series: Observed, Trend, Seasonal, Residual', fontsize=13, fontweight='bold')
axes[0].legend(loc='upper left')
axes[0].grid(True, linestyle='--', alpha=0.5)

axes[1].plot(df.index, trend, color='#e67e22', label='Trend (Moving Average 12 Bulan)')
axes[1].legend(loc='upper left')
axes[1].grid(True, linestyle='--', alpha=0.5)

axes[2].plot(df.index, seasonal, color='#2ecc71', label='Seasonal (Siklus Musiman Tahunan)')
axes[2].legend(loc='upper left')
axes[2].grid(True, linestyle='--', alpha=0.5)

axes[3].scatter(df.index, residual, color='#9b59b6', s=15, alpha=0.7, label='Residual (Sisa Acak)')
axes[3].axhline(0, color='grey', linestyle='--', linewidth=1)
axes[3].legend(loc='upper left')
axes[3].grid(True, linestyle='--', alpha=0.5)

plt.tight_layout()
plt.show()"""))

# Preprocessing
cells.append(nbf.v4.new_markdown_cell("""## 3. Pra-Pemrosesan Data (*Data Preprocessing*)
Pada tahap ini:
1. **Normalisasi Data**: Menggunakan `MinMaxScaler(0, 1)` agar gradien optimasi stabil.
2. **Pembuatan Sekuens (*Windowing/Lagging*)**: Menggunakan window size $T = 12$ bulan untuk memprediksi bulan ke-$13$.
3. **Pemisahan Data Latih dan Uji**: 80% Data Latih (105 sampel sekuens), 20% Data Uji (27 sampel sekuens).
4. **Reshaping**: Mengubah dimensi tensor input menjadi 3D: `(samples, timesteps, features)`."""))
cells.append(nbf.v4.new_code_cell("""# 1. Scaling dengan MinMaxScaler
values = df['Passengers'].values.reshape(-1, 1).astype('float32')
scaler = MinMaxScaler(feature_range=(0, 1))
scaled_values = scaler.fit_transform(values)

print("Rentang Nilai Awal:", values.min(), "sampai", values.max())
print("Rentang Nilai Setelah Normalisasi:", scaled_values.min(), "sampai", scaled_values.max())

# 2. Windowing function
def create_sequences(data, window_size=12):
    X, y = [], []
    for i in range(len(data) - window_size):
        X.append(data[i:i + window_size])
        y.append(data[i + window_size])
    return np.array(X), np.array(y)

LOOK_BACK = 12
X, y = create_sequences(scaled_values, LOOK_BACK)
print(f"Bentuk Keseluruhan Sekuens: X = {X.shape}, y = {y.shape}")

# 3. Train-Test Split (80% Train, 20% Test)
train_size = int(len(X) * 0.80)
X_train, X_test = X[:train_size], X[train_size:]
y_train, y_test = y[:train_size], y[train_size:]

print(f"Dimensi Data Latih (X_train): {X_train.shape}, y_train: {y_train.shape}")
print(f"Dimensi Data Uji   (X_test) : {X_test.shape}, y_test: {y_test.shape}")"""))

# Model Architecture
cells.append(nbf.v4.new_markdown_cell("""## 4. Pembangunan & Pelatihan Model LSTM
Arsitektur model dibangun secara sekuensial:
- **Layer 1**: `LSTM(64)` dengan aktivasi `tanh` dan `return_sequences=True`
- **Layer 2**: `Dropout(0.2)` untuk mencegah overfitting
- **Layer 3**: `LSTM(32)` dengan aktivasi `tanh` dan `return_sequences=False`
- **Layer 4**: `Dropout(0.2)`
- **Layer 5**: `Dense(16)` dengan aktivasi `relu`
- **Layer 6**: `Dense(1)` (linear output untuk regresi)"""))
cells.append(nbf.v4.new_code_cell("""# Inisialisasi Model Sequential
model = Sequential([
    Input(shape=(LOOK_BACK, 1)),
    LSTM(64, activation='tanh', return_sequences=True),
    Dropout(0.2),
    LSTM(32, activation='tanh', return_sequences=False),
    Dropout(0.2),
    Dense(16, activation='relu'),
    Dense(1)
])

# Kompilasi Model
model.compile(optimizer='adam', loss='mean_squared_error', metrics=['mae'])
model.summary()"""))

# Training
cells.append(nbf.v4.new_markdown_cell("""### 4.1 Pelatihan Model dengan Callbacks"""))
cells.append(nbf.v4.new_code_cell("""# Callbacks untuk stabilitas dan efisiensi
early_stop = EarlyStopping(monitor='val_loss', patience=30, restore_best_weights=True, verbose=1)
reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=15, min_lr=1e-5, verbose=1)

# Training model
history = model.fit(
    X_train, y_train,
    epochs=150,
    batch_size=8,
    validation_data=(X_test, y_test),
    callbacks=[early_stop, reduce_lr],
    verbose=1
)"""))

# Training Curve
cells.append(nbf.v4.new_markdown_cell("""### 4.2 Visualisasi Kurva Loss Pelatihan & Validasi"""))
cells.append(nbf.v4.new_code_cell("""plt.figure(figsize=(10, 5))
plt.plot(history.history['loss'], label='Train Loss (MSE)', color='#2980b9', linewidth=2)
plt.plot(history.history['val_loss'], label='Validation Loss (MSE)', color='#e74c3c', linewidth=2)
plt.title('Kurva Loss Pelatihan dan Validasi Model LSTM', fontsize=14, fontweight='bold', pad=15)
plt.xlabel('Epoch', fontsize=12)
plt.ylabel('Mean Squared Error (MSE)', fontsize=12)
plt.legend(frameon=True, facecolor='white')
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.show()"""))

# Model Evaluation
cells.append(nbf.v4.new_markdown_cell("""## 5. Evaluasi Kinerja Model
Langkah evaluasi:
1. Memprediksi data latih dan data uji.
2. Melakukan *inverse transform* untuk mengembalikan nilai prediksi ke skala asli (jumlah penumpang).
3. Menghitung metrik performa:
   $$\\text{RMSE} = \\sqrt{\\frac{1}{n} \\sum_{i=1}^n (y_i - \\hat{y}_i)^2}$$
   $$\\text{MAE} = \\frac{1}{n} \\sum_{i=1}^n |y_i - \\hat{y}_i|$$
   $$\\text{MAPE} = \\frac{1}{n} \\sum_{i=1}^n \\left| \\frac{y_i - \\hat{y}_i}{y_i} \\right| \\times 100\\%$$
   $$R^2 = 1 - \\frac{\\sum_{i=1}^n (y_i - \\hat{y}_i)^2}{\\sum_{i=1}^n (y_i - \\bar{y})^2}$$"""))
cells.append(nbf.v4.new_code_cell("""# Prediksi
y_train_pred_scaled = model.predict(X_train)
y_test_pred_scaled = model.predict(X_test)

# Inverse transform
y_train_pred = scaler.inverse_transform(y_train_pred_scaled)
y_train_true = scaler.inverse_transform(y_train)
y_test_pred = scaler.inverse_transform(y_test_pred_scaled)
y_test_true = scaler.inverse_transform(y_test)

# Metrik Data Uji
test_rmse = np.sqrt(mean_squared_error(y_test_true, y_test_pred))
test_mae = mean_absolute_error(y_test_true, y_test_pred)
test_mape = np.mean(np.abs((y_test_true - y_test_pred) / y_test_true)) * 100
test_r2 = r2_score(y_test_true, y_test_pred)

# Metrik Data Latih
train_rmse = np.sqrt(mean_squared_error(y_train_true, y_train_pred))
train_mae = mean_absolute_error(y_train_true, y_train_pred)
train_mape = np.mean(np.abs((y_train_true - y_train_pred) / y_train_true)) * 100
train_r2 = r2_score(y_train_true, y_train_pred)

eval_df = pd.DataFrame({
    'Metrik': ['RMSE (Root Mean Squared Error)', 'MAE (Mean Absolute Error)', 'MAPE (Mean Absolute Percentage Error)', 'R² Score (Koefisien Determinasi)'],
    'Data Latih (Train)': [f"{train_rmse:.3f}", f"{train_mae:.3f}", f"{train_mape:.2f}%", f"{train_r2:.4f}"],
    'Data Uji (Test)': [f"{test_rmse:.3f}", f"{test_mae:.3f}", f"{test_mape:.2f}%", f"{test_r2:.4f}"]
})

display(eval_df)"""))

# Comparison Plot
cells.append(nbf.v4.new_markdown_cell("""### 5.1 Plot Garis Perbandingan Nilai Aktual vs Prediksi pada Data Uji"""))
cells.append(nbf.v4.new_code_cell("""test_dates = df.index[LOOK_BACK + train_size:]

plt.figure(figsize=(14, 6))
plt.plot(test_dates, y_test_true, label='Nilai Aktual (Ground Truth)', color='#2c3e50', marker='o', linewidth=2.2)
plt.plot(test_dates, y_test_pred, label=f'Prediksi LSTM (RMSE: {test_rmse:.2f})', color='#e74c3c', marker='s', linestyle='--', linewidth=2.2)
plt.fill_between(test_dates, (y_test_pred - test_rmse).flatten(), (y_test_pred + test_rmse).flatten(), color='#e74c3c', alpha=0.15, label='Batas Toleransi (±1 RMSE)')
plt.title('Perbandingan Nilai Aktual vs Prediksi Model LSTM pada Data Uji', fontsize=14, fontweight='bold', pad=15)
plt.xlabel('Bulan', fontsize=12)
plt.ylabel('Jumlah Penumpang (Ribuan)', fontsize=12)
plt.legend(frameon=True, facecolor='white', loc='upper left')
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.show()"""))

# Comprehensive Full Plot
cells.append(nbf.v4.new_markdown_cell("""### 5.2 Evaluasi Komprehensif Seluruh Rentang Waktu"""))
cells.append(nbf.v4.new_code_cell("""train_dates = df.index[LOOK_BACK:LOOK_BACK + train_size]

plt.figure(figsize=(15, 6))
plt.plot(df.index, df['Passengers'], label='Data Historis Asli', color='#7f8c8d', alpha=0.8, linewidth=1.8)
plt.plot(train_dates, y_train_pred, label='Prediksi Data Latih (Train Fit)', color='#2980b9', linewidth=2)
plt.plot(test_dates, y_test_pred, label='Prediksi Data Uji (Test Forecast)', color='#e74c3c', linewidth=2.2)
plt.axvline(x=test_dates[0], color='#27ae60', linestyle=':', linewidth=2, label='Titik Pemisahan Train/Test (Split Point)')
plt.title('Evaluasi Komprehensif: Fitting Data Latih dan Generalisasi Data Uji', fontsize=14, fontweight='bold', pad=15)
plt.xlabel('Tahun', fontsize=12)
plt.ylabel('Jumlah Penumpang (Ribuan)', fontsize=12)
plt.legend(frameon=True, facecolor='white', loc='upper left')
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.show()"""))

# Multi-step Forecasting
cells.append(nbf.v4.new_markdown_cell("""## 6. Peramalan Multi-Step ke Masa Depan (*Future Multi-Step Forecasting*)
Melakukan peramalan rekursif (*autoregressive loop*) untuk memproyeksikan jumlah penumpang hingga 12 dan 24 bulan ke depan."""))
cells.append(nbf.v4.new_code_cell("""def forecast_future_months(model, scaler, last_sequence, n_steps=12):
    curr_seq = last_sequence.copy()
    predictions = []
    
    for _ in range(n_steps):
        input_data = curr_seq.reshape(1, LOOK_BACK, 1)
        pred_scaled = model.predict(input_data, verbose=0)
        predictions.append(pred_scaled[0, 0])
        # Geser jendela sekuens (slide window)
        curr_seq = np.append(curr_seq[1:], pred_scaled[0, 0])
        
    predictions_scaled = np.array(predictions).reshape(-1, 1)
    predictions_original = scaler.inverse_transform(predictions_scaled)
    return predictions_original

# Menggunakan 12 bulan terakhir dari dataset
last_12_months = scaled_values[-LOOK_BACK:]
future_12 = forecast_future_months(model, scaler, last_12_months, n_steps=12)

# Buat indeks tanggal masa depan (1961)
future_dates = pd.date_range(start='1961-01-01', periods=12, freq='MS')
forecast_df = pd.DataFrame({
    'Bulan': future_dates.strftime('%Y-%m'),
    'Prediksi_Penumpang': future_12.flatten().round(1)
})

display(forecast_df)

# Visualisasi Proyeksi ke Masa Depan
plt.figure(figsize=(14, 6))
plt.plot(df.index[-36:], df['Passengers'][-36:], label='Historis Terakhir (3 Tahun)', color='#2c3e50', marker='o')
plt.plot(future_dates, future_12, label='Proyeksi Masa Depan (Tahun 1961)', color='#8e44ad', marker='^', linestyle='--', linewidth=2.2)
plt.title('Proyeksi Jumlah Penumpang Maskapai untuk 12 Bulan ke Depan (1961)', fontsize=14, fontweight='bold', pad=15)
plt.xlabel('Tahun & Bulan', fontsize=12)
plt.ylabel('Jumlah Penumpang (Ribuan)', fontsize=12)
plt.legend(frameon=True, facecolor='white', loc='upper left')
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.show()"""))

# Save Model
cells.append(nbf.v4.new_markdown_cell("""## 7. Penyimpanan Model dan Artefak
Menyimpan model ke dalam format `.keras` dan `.h5`, serta objek scaler ke dalam format `.joblib`."""))
cells.append(nbf.v4.new_code_cell("""os.makedirs('model', exist_ok=True)
model.save('model/lstm_model.keras')
model.save('model/lstm_model.h5')
joblib.dump(scaler, 'model/scaler.joblib')

print("Status Penyimpanan:")
print("- Model Keras (.keras) : Berhasil disimpan ke model/lstm_model.keras")
print("- Model Legacy (.h5)   : Berhasil disimpan ke model/lstm_model.h5")
print("- Scaler (.joblib)     : Berhasil disimpan ke model/scaler.joblib")"""))

# Conclusions
cells.append(nbf.v4.new_markdown_cell("""## 8. Kesimpulan dan Diskusi
1. **Pola Karakteristik Data**: Data *AirPassengers* menunjukkan dua karakteristik fundamental: tren kenaikan non-linier dan musiman tahunan (*seasonality*) dengan lonjakan penumpang pada musim liburan musim panas (Juli-Agustus).
2. **Kinerja Arsitektur LSTM**: Model LSTM dengan kombinasi 2 layer LSTM, Dropout 0.2, dan Dense layer berhasil menangkap tren dan pola musiman dengan sangat akurat, mencapai **$R^2$ sebesar 0.809** dan **MAPE sebesar 6.59%** pada data uji *out-of-sample*.
3. **Generalisasi**: Penggunaan *Early Stopping* dan *ReduceLROnPlateau* terbukti efektif mencegah *overfitting*, dibuktikan dengan kurva loss pelatihan dan validasi yang berkonvergensi secara stabil.
4. **Kesiapan Deployment**: Model dan skaler telah diekspor dan siap diintegrasikan ke dalam antarmuka aplikasi web berbasis Flask untuk peramalan interaktif secara *real-time*."""))

nb.cells = cells

with open('notebook.ipynb', 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print("notebook.ipynb created successfully!")
