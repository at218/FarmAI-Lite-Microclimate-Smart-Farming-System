import pandas as pd
import numpy as np


# Compute Zone Health Score (0–100)
def compute_zone_health(row):
    """
    Calculates a simple health score for a zone based on:
    - Ideal air temperature ~28°C
    - Soil moisture 70–85%
    - Humidity 60–80%
    - Soil temperature ~24–30°C
    Returns numeric 0..100
    """
    # safe access with defaults
    temp = float(row.get('air_temperature', 28.0))
    sm = float(row.get('soil_moisture', 75.0))
    hum = float(row.get('humidity', 70.0))
    soil_t = float(row.get('soil_temperature', 26.0))

    # Normalize toward optimal values (0..1)
    temp_score = max(0.0, 1.0 - abs(temp - 28.0) / 15.0)
    soil_moisture_score = min(max((sm - 40.0) / 45.0, 0.0), 1.0)
    humidity_score = min(max((hum - 40.0) / 60.0, 0.0), 1.0)
    soil_temp_score = max(0.0, 1.0 - abs(soil_t - 26.0) / 12.0)

    # Weighted total
    score = (
        temp_score * 0.30 +
        soil_moisture_score * 0.30 +
        humidity_score * 0.20 +
        soil_temp_score * 0.20
    )
    return float(score * 100.0)


# Rule-based irrigation labels (row-level)
def irrigation_rule(row):
    sm = row.get('soil_moisture', None)
    temp = row.get('air_temperature', None)
    try:
        sm = float(sm)
    except:
        return "Unknown"
    try:
        temp = float(temp)
    except:
        temp = 0.0

    if sm < 70 and temp > 28:
        return "High"
    elif sm < 85:
        return "Medium"
    else:
        return "Low"


def assign_irrigation_labels(df):
    """Applies irrigation_rule to each row and returns a copy with column 'Irrigation_Need_Label'."""
    df2 = df.copy()
    df2['Irrigation_Need_Label'] = df2.apply(irrigation_rule, axis=1)
    return df2


# Season-agnostic crop recommendation (base)
def recommend_crop(zone):
    """
    Basic mapping from zone name to crop list (string).
    Season-specific mapping is done in the page code.
    """
    if zone == "Hot & Dry Zone":
        return "Millet, Sorghum, Groundnut"
    elif zone == "Cool & Moist Zone":
        return "Spinach, Lettuce, Cabbage"
    elif zone == "Rain-Influenced Zone":
        return "Rice, Sugarcane"
    else:
        return "Wheat, Maize, Vegetables"


# Improved irrigation decision using recent-window logic
def compute_zone_irrigation(zone_df, lookback_hours=24,
                            min_threshold=65, avg_threshold=70, medium_threshold=80,
                            temp_threshold=28, recent_rain_threshold=2.0):
    """
    Returns (level, stats) where level in {'High','Medium','Low'} and stats is a dict.
    Uses the last `lookback_hours` of data (if 'timestamp' present) or whole zone_df as fallback.
    """
    if zone_df is None or len(zone_df) == 0:
        return "Low", {'avg_soil_moisture': 0.0, 'min_soil_moisture': 0.0, 'avg_temperature': 0.0, f'rain_last_{lookback_hours}h': 0.0}

    df = zone_df.copy()
    # parse timestamp if present
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        last_ts = df['timestamp'].max()
        if pd.notna(last_ts):
            start = last_ts - pd.Timedelta(hours=lookback_hours)
            recent = df[df['timestamp'] >= start]
            if recent.empty:
                recent = df
        else:
            recent = df
    else:
        recent = df
    # ensure numeric columns exist and coerce
    for c in ['soil_moisture', 'air_temperature', 'rainfall']:
        if c not in recent.columns:
            recent[c] = 0.0
        recent[c] = pd.to_numeric(recent[c], errors='coerce').fillna(method='ffill').fillna(0.0)

    avg_sm = float(recent['soil_moisture'].mean())
    min_sm = float(recent['soil_moisture'].min())
    avg_temp = float(recent['air_temperature'].mean())
    total_rain = float(recent['rainfall'].sum())
    # Decision logic
    if min_sm < min_threshold:
        level = 'High'
    elif (avg_sm < avg_threshold) and (avg_temp > temp_threshold) and (total_rain < recent_rain_threshold):
        level = 'High'
    elif avg_sm < medium_threshold:
        level = 'Medium'
    else:
        level = 'Low'
    stats = {
        'avg_soil_moisture': round(avg_sm, 2),
        'min_soil_moisture': round(min_sm, 2),
        'avg_temperature': round(avg_temp, 2),
        f'rain_last_{lookback_hours}h': round(total_rain, 2)
    }
    return level, stats


# Simple anomaly filter (optional)
def detect_anomalies(df):
    """
    Return rows where values are clearly out-of-bounds (very simple rules).
    """
    cond = (
        (pd.to_numeric(df.get('air_temperature', pd.Series([0]*len(df))), errors='coerce') < 5) |
        (pd.to_numeric(df.get('air_temperature', pd.Series([0]*len(df))), errors='coerce') > 45) |
        (pd.to_numeric(df.get('soil_moisture', pd.Series([0]*len(df))), errors='coerce') < 5) |
        (pd.to_numeric(df.get('soil_moisture', pd.Series([0]*len(df))), errors='coerce') > 100) |
        (pd.to_numeric(df.get('humidity', pd.Series([0]*len(df))), errors='coerce') < 5) |
        (pd.to_numeric(df.get('humidity', pd.Series([0]*len(df))), errors='coerce') > 100)
    )
    return df[cond]
