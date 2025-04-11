# 

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Fungsi analisis yang diperbarui
def analyze_pollution_weekday(df, station_name):
    # Klasifikasi hari
    df['day_type'] = df['date'].apply(lambda x: 'Weekday' if x.weekday() < 5 else 'Weekend')
    
    # Rata-rata harian
    daily_avg = df.groupby(['date', 'day_type'])[['CO', 'NO2']].mean().reset_index()
    
    # Gabungkan hasil
    result = daily_avg.groupby('day_type')[['CO', 'NO2']].mean()
    result['station'] = station_name
    
    return result

@st.cache_data
def load_data():
    # Load data
    dongsi = pd.read_csv('https://github.com/marceloreis/HTI/blob/master/PRSA_Data_20130301-20170228/PRSA_Data_Dongsi_20130301-20170228.csv?raw=true')
    guanyuan = pd.read_csv('https://github.com/marceloreis/HTI/blob/master/PRSA_Data_20130301-20170228/PRSA_Data_Guanyuan_20130301-20170228.csv?raw=true')

    # Preprocessing
    for df in [dongsi, guanyuan]:
        df['date'] = pd.to_datetime(df[['year', 'month', 'day']])
        df.fillna(df.mean(numeric_only=True), inplace=True)
    
    dongsi['station'] = 'Dongsi'
    guanyuan['station'] = 'Guanyuan'
    
    return dongsi, guanyuan

dongsi, guanyuan = load_data()
df = pd.concat([dongsi, guanyuan])

st.header('Tugas Analisis Data Polusi Labib Hakam Fauzi')

# Sidebar: Filter dengan multiselect
st.sidebar.header("Filter Data")
all_years = sorted(df['year'].unique().tolist())
year_options = ['All'] + [str(year) for year in all_years]

# Widget multiselect untuk tahun
selected_year_str = st.sidebar.multiselect(
    "Tahun",
    options=year_options,
    default=['All']
)

# Konversi pilihan tahun
if 'All' in selected_year_str:
    selected_years = all_years
else:
    selected_years = [int(year) for year in selected_year_str]

selected_station = st.sidebar.selectbox("Stasiun", options=df['station'].unique())

# Filter data untuk tab1
filtered_df = df[(df['year'].isin(selected_years)) & (df['station'] == selected_station)]

# Tab untuk visualisasi
tab1, tab2 = st.tabs(["Tren Tahunan", "Hari Kerja vs Akhir Pekan"])

with tab1:
    st.header(f"Tren Polusi di {selected_station}")
    
    # Plot PM2.5 dan PM10 per bulan
    monthly_avg = filtered_df.groupby('month')[['PM2.5', 'PM10']].mean().reset_index()
    
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(data=monthly_avg.melt('month', var_name='Parameter', value_name='Konsentrasi'),
                x='month', y='Konsentrasi', hue='Parameter', ax=ax)
    
    ax.set_title(f"Rata-Rata Bulanan PM2.5 dan PM10 ({', '.join(map(str, selected_years))})")
    ax.set_xlabel("Bulan")
    ax.set_ylabel("Konsentrasi (µg/m³)")
    ax.grid(True)
    plt.xticks(range(1, 13))
    st.pyplot(fig)

with tab2:
    st.header(f"Perbandingan Polusi ({', '.join(map(str, selected_years))})")
    
    # Data untuk tab2
    df_filtered_tab2 = df[df['year'].isin(selected_years)]
    dongsi_tab2 = df_filtered_tab2[df_filtered_tab2['station'] == 'Dongsi']
    guanyuan_tab2 = df_filtered_tab2[df_filtered_tab2['station'] == 'Guanyuan']

    # Analisis data
    dongsi_analysis = analyze_pollution_weekday(dongsi_tab2, 'Dongsi')
    guanyuan_analysis = analyze_pollution_weekday(guanyuan_tab2, 'Guanyuan')
    combined_analysis = pd.concat([dongsi_analysis, guanyuan_analysis]).reset_index()

    # Visualisasi
    fig, ax = plt.subplots(2, 1, figsize=(10, 12))
    palette = {'Weekday': '#2ecc71', 'Weekend': '#e74c3c'}
    
    for i, polutan in enumerate(['CO', 'NO2']):
        sns.barplot(
            data=combined_analysis,
            x='station',
            y=polutan,
            hue='day_type',
            palette=palette,
            ax=ax[i]
        )
        
        ax[i].set_title(f'Rata-rata {polutan}', fontweight='bold')
        ax[i].set_xlabel('')
        ax[i].set_ylabel(f'Konsentrasi {polutan} (µg/m³)')
        ax[i].grid(axis='y', linestyle='--', alpha=0.7)
        
        # Tambahkan label nilai
        for p in ax[i].patches:
            ax[i].annotate(
                f'{p.get_height():.1f}',
                (p.get_x() + p.get_width()/2., p.get_height()),
                ha='center',
                va='center',
                xytext=(0, 10),
                textcoords='offset points'
            )

    plt.tight_layout()
    st.pyplot(fig)

    # Analisis statistik
    st.subheader("Analisis Perbedaan")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Dongsi**")
        st.metric("CO Weekday", f"{dongsi_analysis.loc['Weekday', 'CO']:.1f} µg/m³")
        st.metric("CO Weekend", f"{dongsi_analysis.loc['Weekend', 'CO']:.1f} µg/m³")
        
    with col2:
        st.markdown("**Guanyuan**")
        st.metric("NO2 Weekday", f"{guanyuan_analysis.loc['Weekday', 'NO2']:.1f} µg/m³")
        st.metric("NO2 Weekend", f"{guanyuan_analysis.loc['Weekend', 'NO2']:.1f} µg/m³")

# Menampilkan statistik ringkas
st.sidebar.markdown("### Statistik Ringkas")
st.sidebar.write(f"Rata-rata PM2.5: {filtered_df['PM2.5'].mean():.2f} µg/m³")
st.sidebar.write(f"Rata-rata PM10: {filtered_df['PM10'].mean():.2f} µg/m³")

# Statistik Deskriptif
st.write("### Statistik Deskriptif")
st.write(filtered_df.describe())

# Download Data
st.write("### Download Data yang Difilter")
st.download_button(
    label="Download Data sebagai CSV",
    data=filtered_df.to_csv(index=False).encode('utf-8'),
    file_name='filtered_data.csv',
    mime='text/csv',
)