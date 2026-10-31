import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import joblib

# Set random seed for reproducibility
np.random.seed(42)
import tensorflow as tf
tf.random.set_seed(42)
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau

# Create directories
os.makedirs('model', exist_ok=True)
os.makedirs('static/images', exist_ok=True)
os.makedirs('static/css', exist_ok=True)
os.makedirs('static/js', exist_ok=True)
os.makedirs('templates', exist_ok=True)
os.makedirs('reports/figures', exist_ok=True)

# 1. Load Data
df = pd.read_csv('AirPassengers.csv')
df.columns = ['Month', 'Passengers']
df['Month'] = pd.to_datetime(df['Month'])
df.set_index('Month', inplace=True)
print("Data loaded:", df.shape)

# Save processed dataframe for Flask app
df.to_csv('model/processed_passengers.csv')

# 2. Exploratory Data Analysis Plots
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')

# 2.1 Historical Time Series Plot
plt.figure(figsize=(12, 5))
plt.plot(df.index, df['Passengers'], color='#1f77b4', linewidth=2.2, label='Jumlah Penumpang Bulanan')
plt.title('Tren Historis Jumlah Penumpang Maskapai Internasional (1949 - 1960)', fontsize=14, fontweight='bold', pad=15)
plt.xlabel('Tahun', fontsize=12)
plt.ylabel('Jumlah Penumpang (Ribuan)', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend(frameon=True, facecolor='white', loc='upper left')
plt.tight_layout()
plt.savefig('static/images/eda_timeseries.png', dpi=300)
plt.savefig('reports/figures/eda_timeseries.png', dpi=300)
plt.close()

# 2.2 Seasonality by Month Boxplot
df_eda = df.copy()
df_eda['Year'] = df_eda.index.year
df_eda['Month_Name'] = df_eda.index.strftime('%b')
month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

plt.figure(figsize=(12, 5))
sns.boxplot(x='Month_Name', y='Passengers', data=df_eda, order=month_order, palette='crest')
plt.title('Distribusi Musiman Jumlah Penumpang Berdasarkan Bulan (Seasonality)', fontsize=14, fontweight='bold', pad=15)
plt.xlabel('Bulan', fontsize=12)
plt.ylabel('Jumlah Penumpang (Ribuan)', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.savefig('static/images/eda_monthly_boxplot.png', dpi=300)
plt.savefig('reports/figures/eda_monthly_boxplot.png', dpi=300)
plt.close()

# 2.3 Time Series Decomposition (Manual / Statsmodels)
from scipy.signal import savgol_filter
trend = df['Passengers'].rolling(window=12, center=True).mean()
detrended = df['Passengers'] - trend
seasonal = detrended.groupby(df.index.month).transform('mean')
residual = df['Passengers'] - trend - seasonal

fig, axes = plt.subplots(4, 1, figsize=(12, 10), sharex=True)
axes[0].plot(df.index, df['Passengers'], color='#1f77b4', label='Observed')
axes[0].set_title('Dekomposisi Deret Waktu: Observed, Trend, Seasonal, dan Residual', fontsize=13, fontweight='bold')
axes[0].legend(loc='upper left')
axes[0].grid(True, linestyle='--', alpha=0.5)

axes[1].plot(df.index, trend, color='#e67e22', label='Trend (12-Month Moving Average)')
axes[1].legend(loc='upper left')
axes[1].grid(True, linestyle='--', alpha=0.5)

axes[2].plot(df.index, seasonal, color='#2ecc71', label='Seasonal (Pola Tahunan)')
axes[2].legend(loc='upper left')
axes[2].grid(True, linestyle='--', alpha=0.5)

axes[3].scatter(df.index, residual, color='#9b59b6', s=15, alpha=0.7, label='Residual')
axes[3].axhline(0, color='grey', linestyle='--', linewidth=1)
axes[3].legend(loc='upper left')
axes[3].grid(True, linestyle='--', alpha=0.5)

plt.tight_layout()
plt.savefig('static/images/eda_decomposition.png', dpi=300)
plt.savefig('reports/figures/eda_decomposition.png', dpi=300)
plt.close()

# 3. Data Preprocessing & Windowing
values = df['Passengers'].values.reshape(-1, 1).astype('float32')

# Normalization using MinMaxScaler
scaler = MinMaxScaler(feature_range=(0, 1))
scaled_values = scaler.fit_transform(values)

# Windowing function
def create_sequences(data, window_size=12):
    X, y = [], []
    for i in range(len(data) - window_size):
        X.append(data[i:i + window_size])
        y.append(data[i + window_size])
    return np.array(X), np.array(y)

LOOK_BACK = 12
X, y = create_sequences(scaled_values, LOOK_BACK)
print(f"X shape: {X.shape}, y shape: {y.shape}")

# Split Chronologically: 80% train, 20% test
train_size = int(len(X) * 0.80)
X_train, X_test = X[:train_size], X[train_size:]
y_train, y_test = y[:train_size], y[train_size:]
print(f"X_train: {X_train.shape}, X_test: {X_test.shape}")

# 4. Build LSTM Model
model = Sequential([
    LSTM(64, activation='tanh', return_sequences=True, input_shape=(LOOK_BACK, 1)),
    Dropout(0.2),
    LSTM(32, activation='tanh', return_sequences=False),
    Dropout(0.2),
    Dense(16, activation='relu'),
    Dense(1)
])

model.compile(optimizer='adam', loss='mean_squared_error', metrics=['mae'])
model.summary()

# Callbacks
early_stop = EarlyStopping(monitor='val_loss', patience=30, restore_best_weights=True, verbose=1)
reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=15, min_lr=1e-5, verbose=1)

# Train Model
history = model.fit(
    X_train, y_train,
    epochs=150,
    batch_size=8,
    validation_data=(X_test, y_test),
    callbacks=[early_stop, reduce_lr],
    verbose=1
)

# 5. Training History Plot
plt.figure(figsize=(10, 5))
plt.plot(history.history['loss'], label='Train Loss (MSE)', color='#2980b9', linewidth=2)
plt.plot(history.history['val_loss'], label='Validation Loss (MSE)', color='#e74c3c', linewidth=2)
plt.title('Kurva Loss Pelatihan dan Validasi Model LSTM', fontsize=14, fontweight='bold', pad=15)
plt.xlabel('Epoch', fontsize=12)
plt.ylabel('Mean Squared Error (MSE)', fontsize=12)
plt.legend(frameon=True, facecolor='white')
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.savefig('static/images/training_loss.png', dpi=300)
plt.savefig('reports/figures/training_loss.png', dpi=300)
plt.close()

# 6. Model Evaluation on Test Data
y_train_pred_scaled = model.predict(X_train)
y_test_pred_scaled = model.predict(X_test)

# Inverse transform
y_train_pred = scaler.inverse_transform(y_train_pred_scaled)
y_train_true = scaler.inverse_transform(y_train)
y_test_pred = scaler.inverse_transform(y_test_pred_scaled)
y_test_true = scaler.inverse_transform(y_test)

# Calculate metrics
test_rmse = np.sqrt(mean_squared_error(y_test_true, y_test_pred))
test_mae = mean_absolute_error(y_test_true, y_test_pred)
test_mape = np.mean(np.abs((y_test_true - y_test_pred) / y_test_true)) * 100
test_r2 = r2_score(y_test_true, y_test_pred)

train_rmse = np.sqrt(mean_squared_error(y_train_true, y_train_pred))
train_mae = mean_absolute_error(y_train_true, y_train_pred)
train_mape = np.mean(np.abs((y_train_true - y_train_pred) / y_train_true)) * 100
train_r2 = r2_score(y_train_true, y_train_pred)

metrics = {
    'train_rmse': round(float(train_rmse), 3),
    'train_mae': round(float(train_mae), 3),
    'train_mape': round(float(train_mape), 3),
    'train_r2': round(float(train_r2), 4),
    'test_rmse': round(float(test_rmse), 3),
    'test_mae': round(float(test_mae), 3),
    'test_mape': round(float(test_mape), 3),
    'test_r2': round(float(test_r2), 4),
    'epochs_trained': len(history.history['loss']),
    'look_back': LOOK_BACK,
    'train_samples': int(len(X_train)),
    'test_samples': int(len(X_test))
}

with open('model/metrics.json', 'w') as f:
    json.dump(metrics, f, indent=4)

print("\n--- EVALUATION METRICS ---")
for k, v in metrics.items():
    print(f"{k}: {v}")

# 7. Evaluation Visualizations
# Test dates
test_dates = df.index[LOOK_BACK + train_size:]

plt.figure(figsize=(12, 6))
plt.plot(test_dates, y_test_true, label='Nilai Aktual (Ground Truth)', color='#2c3e50', marker='o', linewidth=2.2)
plt.plot(test_dates, y_test_pred, label=f'Prediksi LSTM (RMSE: {test_rmse:.2f})', color='#e74c3c', marker='s', linestyle='--', linewidth=2.2)
plt.fill_between(test_dates, (y_test_pred - test_rmse).flatten(), (y_test_pred + test_rmse).flatten(), color='#e74c3c', alpha=0.15, label='Batas Toleransi (±1 RMSE)')
plt.title('Perbandingan Nilai Aktual vs Prediksi Model LSTM pada Data Uji', fontsize=14, fontweight='bold', pad=15)
plt.xlabel('Bulan', fontsize=12)
plt.ylabel('Jumlah Penumpang (Ribuan)', fontsize=12)
plt.legend(frameon=True, facecolor='white', loc='upper left')
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.savefig('static/images/model_prediction_test.png', dpi=300)
plt.savefig('reports/figures/model_prediction_test.png', dpi=300)
plt.close()

# Full series plot (Historical + Train Pred + Test Pred)
train_dates = df.index[LOOK_BACK:LOOK_BACK + train_size]

plt.figure(figsize=(14, 6))
plt.plot(df.index, df['Passengers'], label='Data Historis Asli', color='#7f8c8d', alpha=0.8, linewidth=1.8)
plt.plot(train_dates, y_train_pred, label='Prediksi Data Latih (Train Fit)', color='#2980b9', linewidth=2)
plt.plot(test_dates, y_test_pred, label='Prediksi Data Uji (Test Forecast)', color='#e74c3c', linewidth=2.2)
plt.axvline(x=test_dates[0], color='#27ae60', linestyle=':', linewidth=2, label='Titik Pemisahan Train/Test')
plt.title('Evaluasi Komprehensif: Fitting Data Latih dan Generalisasi Data Uji', fontsize=14, fontweight='bold', pad=15)
plt.xlabel('Tahun', fontsize=12)
plt.ylabel('Jumlah Penumpang (Ribuan)', fontsize=12)
plt.legend(frameon=True, facecolor='white', loc='upper left')
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.savefig('static/images/full_series_forecast.png', dpi=300)
plt.savefig('reports/figures/full_series_forecast.png', dpi=300)
plt.close()

# Residuals plot
residuals = y_test_true.flatten() - y_test_pred.flatten()

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
axes[0].scatter(y_test_pred.flatten(), residuals, color='#8e44ad', alpha=0.8, edgecolor='k')
axes[0].axhline(0, color='red', linestyle='--', linewidth=1.5)
axes[0].set_title('Residuals vs Nilai Prediksi', fontsize=12, fontweight='bold')
axes[0].set_xlabel('Nilai Prediksi Penumpang', fontsize=11)
axes[0].set_ylabel('Residual (Aktual - Prediksi)', fontsize=11)
axes[0].grid(True, linestyle='--', alpha=0.6)

sns.histplot(residuals, kde=True, ax=axes[1], color='#16a085', bins=10)
axes[1].axvline(0, color='red', linestyle='--', linewidth=1.5)
axes[1].set_title('Distribusi Residual Kesalahan Prediksi', fontsize=12, fontweight='bold')
axes[1].set_xlabel('Residual', fontsize=11)
axes[1].set_ylabel('Frekuensi', fontsize=11)
axes[1].grid(True, linestyle='--', alpha=0.6)

plt.tight_layout()
plt.savefig('static/images/residuals_distribution.png', dpi=300)
plt.savefig('reports/figures/residuals_distribution.png', dpi=300)
plt.close()

# 8. Save Model and Scaler
model.save('model/lstm_model.h5')
model.save('model/lstm_model.keras')
joblib.dump(scaler, 'model/scaler.joblib')

# Save test predictions for quick display in Flask
test_results_df = pd.DataFrame({
    'Date': test_dates.strftime('%Y-%m'),
    'Actual': y_test_true.flatten(),
    'Predicted': y_test_pred.flatten(),
    'Error': (y_test_true.flatten() - y_test_pred.flatten()),
    'Abs_Error_Pct': np.abs((y_test_true.flatten() - y_test_pred.flatten()) / y_test_true.flatten()) * 100
})
test_results_df.to_csv('model/test_results.csv', index=False)

print("\nModel and artifacts saved successfully!")
