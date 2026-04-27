import streamlit as st
import pandas as pd
from utils import compute_zone_health

st.set_page_config(page_title="Crop Recommendations", layout="wide")
st.title("🌱 Crop Recommendations")

df = pd.read_csv("data/microclimate_clustered_final.csv")

required = {'Cluster Name', 'air_temperature', 'soil_moisture', 'humidity', 'soil_temperature', 'rainfall', 'light_intensity'}
missing = required - set(df.columns)
if missing:
    st.error(f"Dataset is missing required columns: {sorted(list(missing))}")
    st.stop()

season = st.selectbox("Season for recommendations", ["All seasons", "Summer", "Winter"])

crop_map = {
    'Hot & Dry Zone': {
        'Summer': ['Millet', 'Sorghum', 'Groundnut'],
        'Winter': ['Gram', 'Mustard', 'Barley'],
        'All seasons': ['Millet', 'Sorghum', 'Groundnut', 'Gram']
    },
    'Cool & Moist Zone': {
        'Summer': ['Okra', 'Brinjal'],
        'Winter': ['Spinach', 'Lettuce', 'Cabbage'],
        'All seasons': ['Spinach', 'Lettuce', 'Cabbage']
    },
    'Rain-Influenced Zone': {
        'Summer': ['Rice'],
        'Winter': ['Sugarcane'],
        'All seasons': ['Rice', 'Sugarcane']
    },
    'Sunny & Balanced Zone': {
        'Summer': ['Maize', 'Sorghum', 'Pulses'],
        'Winter': ['Wheat', 'Mustard', 'Barley'],
        'All seasons': ['Wheat', 'Maize', 'Vegetables']
    }
}


def irrigation_label(avg_sm, avg_temp):
    if pd.isna(avg_sm):
        return "Unknown"
    if avg_sm < 70 and avg_temp > 28:
        return "🔴 High"
    elif avg_sm < 85:
        return "🟡 Medium"
    else:
        return "🟢 Low"

zones = df['Cluster Name'].unique().tolist()
rows = []
for z in zones:
    zone_df = df[df['Cluster Name'] == z]
    avg_sm = zone_df['soil_moisture'].mean()
    avg_temp = zone_df['air_temperature'].mean()
    avg_hum = zone_df['humidity'].mean()
    avg_soil_temp = zone_df['soil_temperature'].mean()
    avg_light = zone_df['light_intensity'].mean()
    # crop suggestions for chosen season
    crops = crop_map.get(z, {}).get(season, [])
    if not crops:
        crops = crop_map.get(z, {}).get('All seasons', [])
    crops_txt = ", ".join(crops) if crops else "No suggestion"
    # irrigation based on zone average (recommended)
    irr = irrigation_label(avg_sm, avg_temp)
    # health score (avg of rows)
    health_scores = zone_df.apply(compute_zone_health, axis=1)
    mean_health = round(health_scores.mean(), 1)
    rows.append({
        "Zone": z,
        "Recommended Crops": crops_txt,
        "Avg Soil Moisture (%)": round(avg_sm, 2),
        "Avg Air Temp (°C)": round(avg_temp, 2),
        "Irrigation Need": irr,
        "Zone Health (0-100)": mean_health
    })

table = pd.DataFrame(rows)

# Show table and download
st.subheader("Recommendations Table")
st.dataframe(table.style.format({
    "Avg Soil Moisture (%)": "{:.2f}",
    "Avg Air Temp (°C)": "{:.2f}",
    "Zone Health (0-100)": "{:.1f}"
}), use_container_width=True)

csv = table.to_csv(index=False).encode('utf-8')
st.download_button("📥 Download recommendations (CSV)", data=csv, file_name=f"crop_recommendations_{season}.csv", mime='text/csv')

st.markdown("---")
st.subheader("Zone Cards")

# Nicely formatted cards (2 columns)
cols = st.columns(2)
for i, row in table.iterrows():
    col = cols[i % 2]
    zone_name = row['Zone']
    # color the card header based on irrigation need
    irr = row['Irrigation Need']
    if "🔴" in irr:
        header = f"🔴 {zone_name}"
    elif "🟡" in irr:
        header = f"🟡 {zone_name}"
    elif "🟢" in irr:
        header = f"🟢 {zone_name}"
    else:
        header = zone_name

    col.markdown(f"### {header}")
    col.markdown(f"**Crops ({season}):** {row['Recommended Crops']}")
    col.markdown(f"- **Avg soil moisture:** {row['Avg Soil Moisture (%)']} %")
    col.markdown(f"- **Avg air temp:** {row['Avg Air Temp (°C)']} °C")
    col.markdown(f"- **Irrigation need:** {row['Irrigation Need']}")
    # health badge
    h = row['Zone Health (0-100)']
    if h >= 75:
        col.success(f"Health: {h} / 100")
    elif h >= 50:
        col.info(f"Health: {h} / 100")
    else:
        col.warning(f"Health: {h} / 100")
    col.markdown("---")

st.info("Tip: edit `crop_map` in this file to tune crop lists per zone & season.")
