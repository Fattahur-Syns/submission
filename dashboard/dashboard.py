import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load dataset 
@st.cache_data
def load_data():
    df = pd.read_csv("dashboard/main_data.csv", parse_dates=["datetime"])
    return df

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

# Plot visualisasi diagram garis
st.title(f"Tren {polutan} per Tahun di {kota}")
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(annual_data["year"], annual_data[polutan], marker='o', linestyle='-')
ax.set_xlabel("Tahun")
ax.set_ylabel(f"Konsentrasi {polutan}")
ax.set_title(f"Perubahan {polutan} dari Waktu ke Waktu")
ax.grid(True)
st.pyplot(fig)

# Heatmap berdasarkan bulan dan tahun
df_filtered["month"] = df_filtered["datetime"].dt.month
heatmap_data = df_filtered.pivot_table(index="month", columns="year", values=polutan, aggfunc="mean")

st.write("### Heatmap Konsentrasi Polutan")
fig, ax = plt.subplots(figsize=(12, 6))
sns.heatmap(heatmap_data, cmap="coolwarm", annot=True, fmt=".1f", linewidths=0.5, ax=ax)
ax.set_xlabel("Tahun")
ax.set_ylabel("Bulan")
ax.set_title(f"Distribusi {polutan} per Bulan dan Tahun")
st.pyplot(fig)

# Fitur interaktif untuk eksplorasi
# Fitur interaktif untuk eksplorasi
data_selection = st.multiselect("Pilih Kolom Data untuk Ditampilkan", df.columns, default=["datetime", "station", polutan])

# Menampilkan data yang sesuai dengan kota yang dipilih
st.write("### Data yang Dipilih Sesuai Kota")
st.dataframe(df_filtered[data_selection])

st.write("### Kesimpulan Analisis")
with open("notebook.ipynb", "r", encoding="utf-8") as notebook_file:
    notebook_content = notebook_file.read()
    if "Conclusion" in notebook_content:
        kesimpulan_start = notebook_content.find("Conclusion")
        kesimpulan_text = notebook_content[kesimpulan_start:].split("\n", 1)[1]
        st.write("#### Ringkasan Kesimpulan")
        st.write(kesimpulan_text.strip())
    else:
        st.write("Tidak ditemukan kesimpulan dalam notebook.")
