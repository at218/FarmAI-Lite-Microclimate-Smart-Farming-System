import streamlit as st
import pandas as pd
from utils import compute_zone_health

st.title("📋 Zone Summary")

df = pd.read_csv("data/microclimate_clustered_final.csv")

if 'Cluster Name' not in df.columns:
    st.error("Cluster Name column missing. Run clustering first.")
    st.stop()

summary = df.groupby('Cluster Name')[['air_temperature', 'humidity', 'soil_moisture',
                                      'soil_temperature', 'rainfall', 'light_intensity']].mean().round(2)

# add health score to summary
df['__health_score'] = df.apply(compute_zone_health, axis=1)
health_mean = df.groupby('Cluster Name')['__health_score'].mean().round(2)
summary['Avg Health (0-100)'] = health_mean

st.write("### Average environmental conditions per zone (with health score):")
st.dataframe(summary)

# Downloadable CSV
csv = summary.reset_index().to_csv(index=False).encode('utf-8')
st.download_button("Download zone summary CSV", data=csv, file_name="zone_summary.csv", mime='text/csv')
