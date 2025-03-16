import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load dataset dengan caching
@st.cache_data(hash_funcs={pd.DataFrame: lambda _: None})
def load_data():
    df = pd.read_csv("dashboard/main_data.csv", parse_dates=["datetime"])
    return df

df = load_data()

# Sidebar untuk memilih kota dan polutan
st.sidebar.header("Pengaturan Visualisasi")
kota_options = ["Semua Kota"] + list(df["station"].unique())
polutan_options = [col for col in df.columns if col not in ["datetime", "station", "year", "month"]]

kota = st.sidebar.multiselect("Pilih Kota", kota_options, default=["Semua Kota"])
polutan = st.sidebar.multiselect("Pilih Polutan", polutan_options, default=["PM2.5"])

# Filter data berdasarkan pilihan
df_filtered = df.copy()

if "Semua Kota" not in kota:
    df_filtered = df[df["station"].isin(kota)]

# Pastikan ada data setelah filtering
if df_filtered.empty:
    st.warning("Tidak ada data yang tersedia untuk filter yang dipilih.")
    st.stop()

# Tambahkan kolom tahun dan bulan
df_filtered["year"] = df_filtered["datetime"].dt.year
df_filtered["month"] = df_filtered["datetime"].dt.month

# Menghitung rata-rata per tahun untuk setiap kota dan polutan
annual_pollutants = df_filtered.groupby(["year", "station"])[polutan].mean().reset_index()
annual_pollutants.set_index("year", inplace=True)

# Fungsi untuk menampilkan tren polutan per tahun tanpa subplot berlebih
def plot_all_cities(data, pollutants):
    """Plot subplot jika semua kota dipilih"""
    num_plots = len(pollutants)
    rows = (num_plots + 1) // 2  # Menentukan jumlah baris subplot
    cols = 2 if num_plots > 1 else 1  # Menyesuaikan kolom
    
    fig, axes = plt.subplots(rows, cols, figsize=(16, 5 * rows))
    axes = axes.flatten() if num_plots > 1 else [axes]  # Pastikan axes selalu list

    for i, pollutant in enumerate(pollutants):
        ax = axes[i]
        for station in data['station'].unique():
            subset = data[data['station'] == station]
            ax.plot(subset.index, subset[pollutant], marker='o', linestyle='-', label=station)

        ax.set_title(f'Tren {pollutant} per Tahun')
        ax.set_xlabel("Tahun")
        ax.set_ylabel(f"Konsentrasi {pollutant}")
        ax.grid(alpha=0.3)
        ax.legend(title='Stasiun')

    # Hapus subplot yang tidak digunakan
    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])

    plt.tight_layout()
    st.pyplot(fig)

def plot_single_city(data, pollutants):
    """Plot per polutan jika hanya beberapa kota dipilih"""
    for pollutant in pollutants:
        fig, ax = plt.subplots(figsize=(12, 6))
        for station in data['station'].unique():
            subset = data[data['station'] == station]
            ax.plot(subset.index, subset[pollutant], marker='o', linestyle='-', label=station)

        ax.set_title(f'Tren {pollutant} per Tahun')
        ax.set_xlabel("Tahun")
        ax.set_ylabel(f"Konsentrasi {pollutant}")
        ax.grid(alpha=0.3)
        ax.legend(title='Stasiun')

        st.pyplot(fig)

# Menampilkan grafik berdasarkan pilihan
st.title("Visualisasi Data Polusi Udara")

if "Semua Kota" in kota:
    if "Semua Polutan" in polutan:
        plot_all_cities(annual_pollutants, polutan_options[1:])
    else:
        plot_all_cities(annual_pollutants, polutan)
else:
    if "Semua Polutan" in polutan:
        plot_single_city(annual_pollutants, polutan_options[1:])
    else:
        plot_single_city(annual_pollutants, polutan)

# Tampilkan heatmap korelasi
st.write("## Heatmap Korelasi Polutan dan Parameter Cuaca")
correlation = df_filtered.select_dtypes(include=["number"]).corr()

fig, ax = plt.subplots(figsize=(12, 8))
sns.heatmap(correlation, annot=True, fmt='.2f', cmap="coolwarm", ax=ax)
plt.title(f"Heatmap Korelasi ({', '.join(kota) if kota else 'Semua Kota'})")
st.pyplot(fig)

# Tampilkan tabel korelasi
st.write("### Tabel Korelasi")
st.dataframe(correlation)

# Tampilkan data yang difilter
data_selection = st.multiselect("Pilih Kolom Data untuk Ditampilkan", df.columns, default=["datetime", "station"] + polutan)

# Pastikan hanya kolom yang tersedia yang ditampilkan
available_columns = [col for col in data_selection if col in df_filtered.columns]

st.write("### Data yang Dipilih")
st.dataframe(df_filtered[available_columns])
