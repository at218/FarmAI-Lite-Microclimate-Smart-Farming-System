import streamlit as st
import pandas as pd

st.title("💧 Irrigation Advisor")

df = pd.read_csv("data/microclimate_clustered_final.csv")


def irrigation_need(row):
    if row['soil_moisture'] < 70:
        return "🔴 High"
    elif row['soil_moisture'] < 85:
        return "🟡 Medium"
    else:
        return "🟢 Low"

df['Irrigation Need'] = df.apply(irrigation_need, axis=1)

st.dataframe(df[['Cluster Name', 'air_temperature', 'soil_moisture',
                 'humidity', 'Irrigation Need']].head(50))
