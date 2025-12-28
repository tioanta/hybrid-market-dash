import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from datetime import timedelta
import config
import market_analysis

st.set_page_config(
    page_title="Market Forecast Dashboard",
    page_icon="📈",
    layout="wide"
)

# --- CSS CUSTOM UNTUK BERITA ---
st.markdown("""
<style>
    .news-card {
        padding: 15px;
        border-radius: 10px;
        background-color: #262730;
        margin-bottom: 10px;
        border-left: 5px solid #ff4b4b;
    }
    .news-title {
        font-size: 16px;
        font-weight: bold;
        color: #ffffff;
        text-decoration: none;
    }
    .news-date {
        font-size: 12px;
        color: #aaaaaa;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=3600)
def load_data(ticker, keyword):
    df, current, pred = market_analysis.get_technical_forecast(ticker)
    
    # Unpack 3 value sekarang (Score, Label, News List)
    sentiment_score, sentiment_label, news_list = market_analysis.get_news_sentiment(keyword)
    
    signal, change, reason = market_analysis.get_hybrid_signal(current, pred, sentiment_score)
    
    return df, current, pred, sentiment_score, sentiment_label, news_list, signal, change, reason

st.title("🤖 Hybrid Market Intelligence Dashboard")
st.markdown("Analisa otomatis **Teknikal (Prophet)** + **Sentimen Berita (NLP)** untuk Forex & Saham.")
st.markdown("---")

st.sidebar.header("Pilih Aset")
selected_asset = st.sidebar.selectbox(
    "Mata Uang / Saham:",
    list(config.ASSETS.keys())
)

if st.sidebar.button("🔄 Refresh Data Real-time"):
    st.cache_data.clear()

info = config.ASSETS[selected_asset]
with st.spinner(f"Sedang menganalisa {selected_asset}..."):
    try:
        df, current, pred, sent_score, sent_label, news_list, signal, change, reason = load_data(info['ticker'], info['keyword'])
        
        if df is None:
            st.error("Gagal mengambil data dari Yahoo Finance.")
            st.stop()

        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("Harga Saat Ini", f"{current:,.0f}")
        with col2: st.metric("Prediksi Besok", f"{pred:,.0f}", delta=change)
        with col3:
            color = "off"
            if "BUY" in signal: color = "normal"
            elif "SELL" in signal: color = "inverse"
            st.metric("Rekomendasi AI", signal, delta=reason, delta_color=color)
        with col4: st.metric("Sentimen Berita", sent_label, f"Score: {sent_score:.2f}")

        # --- GRAFIK ---
        st.subheader(f"Grafik Pergerakan {selected_asset}")
        df_chart = df.tail(180)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_chart['ds'], y=df_chart['y'], mode='lines', name='Historis', line=dict(color='#00B4D8', width=2)))
        pred_date = df_chart['ds'].iloc[-1] + timedelta(days=1)
        fig.add_trace(go.Scatter(x=[pred_date], y=[pred], mode='markers+text', name='Prediksi Besok', marker=dict(color='#FF9F1C', size=12), text=[f"{pred:,.0f}"], textposition="top center"))
        fig.update_layout(template="plotly_dark", height=500, hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)

        # --- BAGIAN BERITA (BARU) ---
        st.markdown("---")
        st.subheader(f"📰 Top 5 Berita Terkait: {selected_asset}")
        
        if news_list:
            col_news1, col_news2 = st.columns([2, 1]) # Layout 2 kolom (Kiri berita, Kanan info)
            
            with col_news1:
                for news in news_list:
                    # Tampilkan berita dengan Card Style
                    st.markdown(f"""
                    <div class="news-card">
                        <a href="{news['link']}" target="_blank" class="news-title">{news['title']}</a>
                        <br>
                        <span class="news-date">📅 {news['published']}</span>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col_news2:
                st.info(f"""
                **Tentang Sentimen:**
                AI membaca judul dari 5 berita di samping dan memberikan skor **{sent_score:.2f}**.
                
                * Skor > 0.1 : Berita Positif 🟢
                * Skor < -0.1 : Berita Negatif 🔴
                * Lainnya : Netral ⚪
                """)
        else:
            st.warning("Tidak ditemukan berita terbaru untuk aset ini dalam 2 hari terakhir.")

    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")
