import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from utils import compute_zone_health

st.title("🔍 Zone Explorer")

df = pd.read_csv("data/microclimate_clustered_final.csv")

features = [
    'air_temperature',
    'humidity',
    'soil_moisture',
    'soil_temperature',
    'rainfall',
    'light_intensity'
]

if 'Cluster Name' not in df.columns:
    st.error("Cluster Name column missing. Run clustering first.")
    st.stop()

zones = df['Cluster Name'].unique()
selected_zone = st.selectbox("Select a zone:", zones)

zone_data = df[df['Cluster Name'] == selected_zone]

st.write(f"### 📊 Normalized Microclimate Features for **{selected_zone}**")

# ---- RAW AVERAGES ----
avg_raw = zone_data[features].mean().round(2)

# ---- GLOBAL NORMALIZATION (0–1) ----
global_min = df[features].min()
global_max = df[features].max()
global_range = (global_max - global_min).replace(0, 1e-6)
avg_normalized = ((avg_raw - global_min) / global_range).clip(0, 1)

# ---- PLOT ONLY NORMALIZED VALUES ----
fig, ax = plt.subplots(figsize=(10, 4))
avg_normalized.plot(kind='bar', ax=ax, color='mediumseagreen')
ax.set_title(f"Normalized Microclimate Features (0–1 Scale) — {selected_zone}")
ax.set_ylabel("Normalized Value")
ax.tick_params(axis='x', rotation=30)
for i, (norm_v) in enumerate(avg_normalized.values):
    ax.text(i, min(norm_v + 0.03, 1.05), f"{norm_v:.2f}", ha='center', fontsize=10)
plt.ylim(0, 1.15)
plt.tight_layout()
st.pyplot(fig)

# ----- Zone Health Score -----
st.markdown("---")
st.subheader("🩺 Zone Health Score")
health_scores = zone_data.apply(compute_zone_health, axis=1)
mean_health = health_scores.mean()
if mean_health >= 75:
    st.success(f"Healthy — Score: {mean_health:.1f}/100")
elif mean_health >= 50:
    st.info(f"Moderate — Score: {mean_health:.1f}/100")
else:
    st.warning(f"Attention Needed — Score: {mean_health:.1f}/100")
st.progress(int(np.clip(mean_health, 0, 100)))

# ----- WHAT-IF SIMULATOR -----
st.markdown("---")
st.subheader("🔮 What-If Simulator (Hypothetical)")

st.write("Adjust temperature or rainfall to simulate effects on health and irrigation (demo only).")

col1, col2 = st.columns(2)
with col1:
    temp_delta = st.slider("Temperature change (Δ°C)", min_value=-5.0, max_value=5.0, value=0.0, step=0.5)
with col2:
    rain_delta = st.slider("Rainfall change (Δ mm)", min_value=-5.0, max_value=20.0, value=0.0, step=0.5)

# representative baseline = zone averages
sim = avg_raw.copy()
sim['air_temperature'] = sim['air_temperature'] + temp_delta
sim['rainfall'] = max(0, sim['rainfall'] + rain_delta)
# approximate: rainfall increases soil moisture, temperature reduces it
sim['soil_moisture'] = np.clip(sim['soil_moisture'] + (rain_delta * 2.0) - (temp_delta * 0.8), 0, 100)
sim['humidity'] = np.clip(sim['humidity'] + (rain_delta * 1.0) - (temp_delta * 0.5), 0, 100)
sim['soil_temperature'] = sim['soil_temperature'] + temp_delta * 0.6

sim_health = compute_zone_health(sim)
# irrigation rule (same logic)
if sim['soil_moisture'] < 70 and sim['air_temperature'] > 28:
    sim_irrigation = 'High'
elif sim['soil_moisture'] < 85:
    sim_irrigation = 'Medium'
else:
    sim_irrigation = 'Low'

st.markdown("#### Simulated results")
st.write(f"- Health score (simulated): **{sim_health:.1f}/100**")
st.write(f"- Irrigation need (simulated): **{sim_irrigation}**")

sim_display = sim.round(2).to_frame(name='Simulated Value').reset_index().rename(columns={'index':'Feature'})
st.table(sim_display)
