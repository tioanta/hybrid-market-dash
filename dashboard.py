import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from datetime import timedelta
import config
import market_analysis

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Market Forecast Dashboard",
    page_icon="📈",
    layout="wide"
)

# --- FUNGSI CACHE (Agar tidak lambat reload data terus) ---
@st.cache_data(ttl=3600) # Data disimpan selama 1 jam
def load_data(ticker, keyword):
    # 1. Ambil Data Teknikal
    df, current, pred = market_analysis.get_technical_forecast(ticker)
    
    # 2. Ambil Data Sentimen
    sentiment_score, sentiment_label = market_analysis.get_news_sentiment(keyword)
    
    # 3. Hitung Sinyal
    signal, change, reason = market_analysis.get_hybrid_signal(current, pred, sentiment_score)
    
    return df, current, pred, sentiment_score, sentiment_label, signal, change, reason

# --- UI DASHBOARD ---
st.title("🤖 Hybrid Market Intelligence Dashboard")
st.markdown("Analisa otomatis **Teknikal (Prophet)** + **Sentimen Berita (NLP)** untuk Forex & Saham.")
st.markdown("---")

# Sidebar untuk memilih Aset
st.sidebar.header("Pilih Aset")
selected_asset = st.sidebar.selectbox(
    "Mata Uang / Saham:",
    list(config.ASSETS.keys())
)

# Tombol Refresh Manual
if st.sidebar.button("🔄 Refresh Data Real-time"):
    st.cache_data.clear()

# Load Data Aset Terpilih
info = config.ASSETS[selected_asset]
with st.spinner(f"Sedang menganalisa {selected_asset}..."):
    try:
        df, current, pred, sent_score, sent_label, signal, change, reason = load_data(info['ticker'], info['keyword'])
        
        if df is None:
            st.error("Gagal mengambil data dari Yahoo Finance.")
            st.stop()

        # --- BAGIAN 1: KARTU METRIK UTAMA ---
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Harga Saat Ini", f"{current:,.0f}", delta=None)
        
        with col2:
            st.metric("Prediksi Besok", f"{pred:,.0f}", delta=change)
        
        with col3:
            # Warna Sinyal
            color = "off"
            if "BUY" in signal: color = "normal" # Hijau di Streamlit default
            elif "SELL" in signal: color = "inverse" # Merah
            st.metric("Rekomendasi AI", signal, delta=reason, delta_color=color)

        with col4:
            st.metric("Sentimen Berita", sent_label, f"Score: {sent_score:.2f}")

        # --- BAGIAN 2: GRAFIK INTERAKTIF (PLOTLY) ---
        st.subheader(f"Grafik Pergerakan {selected_asset}")
        
        # Filter data 6 bulan terakhir biar enak dilihat
        df_chart = df.tail(180)
        
        fig = go.Figure()
        
        # Garis Historis
        fig.add_trace(go.Scatter(
            x=df_chart['ds'], y=df_chart['y'],
            mode='lines', name='Historis',
            line=dict(color='#00B4D8', width=2)
        ))
        
        # Titik Prediksi
        pred_date = df_chart['ds'].iloc[-1] + timedelta(days=1)
        fig.add_trace(go.Scatter(
            x=[pred_date], y=[pred],
            mode='markers+text', name='Prediksi Besok',
            marker=dict(color='#FF9F1C', size=12),
            text=[f"{pred:,.0f}"], textposition="top center"
        ))

        fig.update_layout(
            template="plotly_dark",
            height=500,
            hovermode="x unified"
        )
        
        st.plotly_chart(fig, use_container_width=True)

        # --- BAGIAN 3: PENJELASAN ---
        st.info(f"""
        **Analisa Detail:**
        AI memprediksi harga **{selected_asset}** akan bergerak sebesar **{change}** besok. 
        Kombinasi grafik teknikal dan sentimen berita ({sent_label}) menghasilkan sinyal **{signal}**.
        
        *Disclaimer: Not Financial Advice.*
        """)

    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")
