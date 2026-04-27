import streamlit as st
import pandas as pd
from utils import compute_zone_health

st.set_page_config(page_title="FarmAI Lite", layout="wide")

st.title("🌾 FarmAI Lite – Smart Microclimate Dashboard")
st.write("A simplified smart farming system using microclimate zoning and rule-based intelligence.")

# Load data
df = pd.read_csv("data/microclimate_clustered_final.csv")

# Summary of zones
if 'Cluster Name' not in df.columns:
    st.error("Cluster Name not found in dataset. Please run clustering step first.")
else:
    zone_counts = df['Cluster Name'].value_counts()

    st.subheader("📊 Zone Overview")
    st.bar_chart(zone_counts)

    st.write("### Zone Types Detected:")
    for zone in zone_counts.index:
        st.write(f"- **{zone}**: {zone_counts[zone]} readings")

    # Zone health summary (average health per zone)
    st.markdown("---")
    st.subheader("🩺 Zone Health Summary (avg)")

    # compute health per row then mean by zone
    df['__health_score'] = df.apply(compute_zone_health, axis=1)
    health_summary = df.groupby('Cluster Name')['__health_score'].mean().round(2).reset_index()
    health_summary = health_summary.rename(columns={'__health_score': 'Avg Health (0-100)'})
    st.dataframe(health_summary)

    # quick top/bottom
    best = health_summary.sort_values('Avg Health (0-100)', ascending=False).iloc[0]
    worst = health_summary.sort_values('Avg Health (0-100)', ascending=True).iloc[0]
    st.markdown(f"**Best zone (avg health):** {best['Cluster Name']} — {best['Avg Health (0-100)']}")
    st.markdown(f"**Zone needing attention (avg health):** {worst['Cluster Name']} — {worst['Avg Health (0-100)']}")
