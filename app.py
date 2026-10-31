import os
import json
import numpy as np
import pandas as pd
from flask import Flask, render_template, request, jsonify
import joblib

# Suppress TensorFlow verbose logging
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import tensorflow as tf

app = Flask(__name__)

# Base directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, 'model')

# Global variables for caching
_model = None
_scaler = None
_df_historical = None
_metrics = None
_test_results = None

def get_resources():
    global _model, _scaler, _df_historical, _metrics, _test_results
    if _model is None:
        model_path = os.path.join(MODEL_DIR, 'lstm_model.keras')
        if not os.path.exists(model_path):
            model_path = os.path.join(MODEL_DIR, 'lstm_model.h5')
        _model = tf.keras.models.load_model(model_path)
    
    if _scaler is None:
        scaler_path = os.path.join(MODEL_DIR, 'scaler.joblib')
        _scaler = joblib.load(scaler_path)
        
    if _df_historical is None:
        data_path = os.path.join(MODEL_DIR, 'processed_passengers.csv')
        _df_historical = pd.read_csv(data_path)
        _df_historical['Month'] = pd.to_datetime(_df_historical['Month'])
        
    if _metrics is None:
        metrics_path = os.path.join(MODEL_DIR, 'metrics.json')
        with open(metrics_path, 'r') as f:
            _metrics = json.load(f)
            
    if _test_results is None:
        test_path = os.path.join(MODEL_DIR, 'test_results.csv')
        _test_results = pd.read_csv(test_path)
        
    return _model, _scaler, _df_historical, _metrics, _test_results

# Helper for multi-step autoregressive forecasting
def autoregressive_forecast(model, scaler, last_12_vals, horizon=12, scenario='standard'):
    curr_seq = np.array(last_12_vals).reshape(-1, 1).astype('float32')
    # If unscaled, scale it
    if np.max(curr_seq) > 1.0 or np.min(curr_seq) < 0.0:
        curr_seq_scaled = scaler.transform(curr_seq)
    else:
        curr_seq_scaled = curr_seq.copy()
        
    predictions_scaled = []
    window = curr_seq_scaled.copy()
    
    for _ in range(horizon):
        x_input = window[-12:].reshape(1, 12, 1)
        pred = model.predict(x_input, verbose=0)
        predictions_scaled.append(pred[0, 0])
        window = np.append(window, pred[0, 0])
        
    preds_orig = scaler.inverse_transform(np.array(predictions_scaled).reshape(-1, 1)).flatten()
    
    # Apply scenario adjustments if requested
    # Standard: unchanged
    # Optimistic: +5% to +10% gradual growth factor
    # Conservative: -5% to -10% gradual reduction factor
    results = []
    for i, val in enumerate(preds_orig):
        factor = (i + 1) / horizon
        if scenario == 'optimistic':
            adj_val = val * (1 + 0.08 * factor)
        elif scenario == 'pessimistic':
            adj_val = val * (1 - 0.08 * factor)
        else:
            adj_val = val
            
        rmse_error = _metrics.get('test_rmse', 35.0) if _metrics else 35.0
        margin = rmse_error * np.sqrt(1 + 0.05 * i)
        
        results.append({
            'step': i + 1,
            'forecast': round(float(adj_val), 1),
            'lower_bound': max(0.0, round(float(adj_val - margin), 1)),
            'upper_bound': round(float(adj_val + margin), 1)
        })
        
    return results

@app.route('/')
def index():
    model, scaler, df, metrics, test_results = get_resources()
    
    # Calculate executive summary stats
    latest_month = df['Month'].iloc[-1].strftime('%B %Y')
    latest_passengers = int(df['Passengers'].iloc[-1])
    min_passengers = int(df['Passengers'].min())
    max_passengers = int(df['Passengers'].max())
    total_records = len(df)
    
    # Historical recent 12 months for quick simulation
    recent_12 = df.tail(12).to_dict(orient='records')
    for r in recent_12:
        r['Month_Str'] = r['Month'].strftime('%Y-%m')
        
    return render_template(
        'index.html',
        metrics=metrics,
        latest_month=latest_month,
        latest_passengers=latest_passengers,
        min_passengers=min_passengers,
        max_passengers=max_passengers,
        total_records=total_records,
        recent_12=recent_12
    )

@app.route('/explore')
def explore():
    _, _, df, metrics, _ = get_resources()
    
    # Summary stats
    stats = {
        'mean': round(df['Passengers'].mean(), 1),
        'std': round(df['Passengers'].std(), 1),
        'min': df['Passengers'].min(),
        'max': df['Passengers'].max(),
        'q25': df['Passengers'].quantile(0.25),
        'median': df['Passengers'].median(),
        'q75': df['Passengers'].quantile(0.75),
    }
    
    # Monthly averages across all years
    df_copy = df.copy()
    df_copy['Month_Num'] = df_copy['Month'].dt.month
    monthly_avg = df_copy.groupby('Month_Num')['Passengers'].mean().round(1).tolist()
    
    records = df.tail(24).copy()
    records['Month_Str'] = records['Month'].dt.strftime('%Y-%m')
    records_list = records.to_dict(orient='records')
    
    return render_template(
        'explore.html',
        stats=stats,
        monthly_avg=monthly_avg,
        records=records_list
    )

@app.route('/evaluation')
def evaluation():
    _, _, df, metrics, test_results = get_resources()
    test_data_table = test_results.to_dict(orient='records')
    return render_template(
        'evaluation.html',
        metrics=metrics,
        test_data=test_data_table
    )

@app.route('/forecast')
def forecast_page():
    _, _, df, metrics, _ = get_resources()
    recent_12 = df.tail(12).copy()
    recent_12['Month_Str'] = recent_12['Month'].dt.strftime('%Y-%m')
    recent_list = recent_12.to_dict(orient='records')
    last_12_vals_str = ",".join(map(str, recent_12['Passengers'].tolist()))
    
    return render_template(
        'forecast.html',
        recent_list=recent_list,
        last_12_vals_str=last_12_vals_str,
        metrics=metrics
    )

@app.route('/about')
def about():
    _, _, _, metrics, _ = get_resources()
    return render_template('about.html', metrics=metrics)

# API Endpoints
@app.route('/api/historical')
def api_historical():
    _, _, df, _, _ = get_resources()
    labels = df['Month'].dt.strftime('%Y-%m').tolist()
    values = df['Passengers'].tolist()
    return jsonify({
        'labels': labels,
        'values': values
    })

@app.route('/api/evaluation-data')
def api_evaluation_data():
    _, _, _, metrics, test_results = get_resources()
    return jsonify({
        'metrics': metrics,
        'labels': test_results['Date'].tolist(),
        'actual': test_results['Actual'].tolist(),
        'predicted': test_results['Predicted'].round(1).tolist(),
        'error': test_results['Error'].round(1).tolist()
    })

@app.route('/api/forecast', methods=['POST', 'GET'])
def api_forecast():
    model, scaler, df, _, _ = get_resources()
    
    if request.method == 'POST':
        data = request.get_json() or {}
        horizon = int(data.get('horizon', 12))
        scenario = data.get('scenario', 'standard')
        input_sequence = data.get('sequence', None)
    else:
        horizon = int(request.args.get('horizon', 12))
        scenario = request.args.get('scenario', 'standard')
        input_sequence = None
        
    horizon = max(1, min(36, horizon))
    
    if input_sequence and len(input_sequence) == 12:
        try:
            last_12 = [float(x) for x in input_sequence]
        except Exception:
            last_12 = df['Passengers'].tail(12).tolist()
    else:
        last_12 = df['Passengers'].tail(12).tolist()
        
    # Generate future dates starting from next month of dataset
    last_date = df['Month'].iloc[-1]
    future_dates = pd.date_range(start=last_date + pd.DateOffset(months=1), periods=horizon, freq='MS')
    future_labels = future_dates.strftime('%Y-%m').tolist()
    
    forecast_results = autoregressive_forecast(model, scaler, last_12, horizon=horizon, scenario=scenario)
    
    for i, res in enumerate(forecast_results):
        res['date'] = future_labels[i]
        
    # Also attach the recent 12 historical points for smooth continuous charting
    recent_labels = df['Month'].tail(12).dt.strftime('%Y-%m').tolist()
    recent_values = df['Passengers'].tail(12).tolist()
    
    return jsonify({
        'status': 'success',
        'horizon': horizon,
        'scenario': scenario,
        'recent_history': {
            'labels': recent_labels,
            'values': recent_values
        },
        'forecast': forecast_results
    })

if __name__ == '__main__':
    # Initialize resources
    get_resources()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
