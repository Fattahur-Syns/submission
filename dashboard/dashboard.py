import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load dataset (gantilah dengan lokasi file yang sesuai)
@st.cache_data
def load_data():
    all_df = pd.read_csv("all_data.csv", parse_dates=["datetime"])
    return all_df

df = load_data()

# Sidebar untuk memilih kota dan polutan
st.sidebar.header("Pengaturan Visualisasi")
kota = st.sidebar.selectbox("Pilih Kota", df["station"].unique())
polutan = st.sidebar.selectbox("Pilih Polutan", ["PM2.5", "PM10", "SO2", "NO2", "CO", "O3"])

# Filter data berdasarkan pilihan
df_filtered = df[df["station"] == kota]
df_filtered["year"] = df_filtered["datetime"].dt.year

# Hitung rata-rata tahunan untuk polutan yang dipilih
annual_data = df_filtered.groupby("year")[polutan].mean().reset_index()

# Plot visualisasi
st.title(f"Tren {polutan} per Tahun di {kota}")
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(annual_data["year"], annual_data[polutan], marker='o', linestyle='-')
ax.set_xlabel("Tahun")
ax.set_ylabel(f"Konsentrasi {polutan}")
ax.set_title(f"Perubahan {polutan} dari Waktu ke Waktu")
ax.grid(True)
st.pyplot(fig)

st.write("### Data Rata-rata Tahunan")
st.dataframe(annual_data)
