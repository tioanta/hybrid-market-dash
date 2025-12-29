import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from datetime import timedelta
import config
import market_analysis

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Hybrid Market Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- FUNGSI CSS DINAMIS UNTUK BERITA ---
def get_dynamic_css(sentiment_color):
    return f"""
    <style>
        .news-card {{
            padding: 15px;
            border-radius: 12px;
            background-color: #1E1E24;
            margin-bottom: 12px;
            border-left: 6px solid {sentiment_color};
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }}
        .news-card:hover {{
            transform: translateY(-3px);
        }}
        .news-title {{
            font-size: 16px;
            font-weight: 600;
            color: #EAEAEA;
            text-decoration: none;
            display: block;
            margin-bottom: 8px;
        }}
        .news-title:hover {{
            color: #4EA8DE;
        }}
        .news-date {{
            font-size: 12px;
            color: #888888;
            font-style: italic;
        }}
        .signal-box {{
            padding: 25px;
            border-radius: 20px;
            text-align: center;
            margin-bottom: 25px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}
        .metric-container {{
             background-color: #1E1E24;
             padding: 20px;
             border-radius: 15px;
             text-align: center;
             border: 1px solid #333;
        }}
    </style>
    """

# --- FUNGSI LOAD DATA (CACHE) ---
@st.cache_data(ttl=3600)
def load_data(ticker, keyword):
    df, current, pred = market_analysis.get_technical_forecast(ticker)
    sentiment_score, sentiment_label, news_list = market_analysis.get_news_sentiment(keyword)
    signal, change, reason = market_analysis.get_hybrid_signal(current, pred, sentiment_score)
    return df, current, pred, sentiment_score, sentiment_label, news_list, signal, change, reason

# --- MAIN DASHBOARD ---
st.title("⚡ Hybrid Market Intelligence")
st.markdown("### *Technical Data + News Sentiment Analysis*")

# --- SIDEBAR ---
st.sidebar.header("🎯 Kontrol Aset")
selected_asset = st.sidebar.selectbox(
    "Pilih Mata Uang / Saham:",
    list(config.ASSETS.keys()),
    index=0
)

st.sidebar.markdown("---")
if st.sidebar.button("🔄 Refresh Data Real-time", type="primary"):
    st.cache_data.clear()
    st.rerun() # <--- PERBAIKAN DI SINI (Sebelumnya st.experimental_rerun)

st.sidebar.markdown("---")
st.sidebar.info(
    """
    **Tentang Dashboard:**
    Dashboard ini menggabungkan prediksi teknikal (Prophet) dengan analisis sentimen berita (NLP) untuk memberikan sinyal hybrid.
    
    *Not Financial Advice.*
    """
)

# --- LOAD DATA ASET TERPILIH ---
info = config.ASSETS[selected_asset]

with st.spinner(f"🤖 Sedang menganalisa jutaan data untuk {selected_asset}..."):
    try:
        df, current, pred, sent_score, sent_label, news_list, signal, change, reason = load_data(info['ticker'], info['keyword'])
        
        if df is None:
            st.error("Gagal mengambil data dari Yahoo Finance. Silakan refresh.")
            st.stop()

        # Tentukan Warna Tema berdasarkan Sinyal & Sentimen
        signal_color_bg = "#333333" 
        signal_icon = "⚖️"
        if "BUY" in signal:
            signal_color_bg = "rgba(46, 204, 113, 0.2)"
            signal_icon = "🚀"
        elif "SELL" in signal:
            signal_color_bg = "rgba(231, 76, 60, 0.2)"
            signal_icon = "🔻"

        sent_color_hex = "#95a5a6"
        if sent_score > 0.1: sent_color_hex = "#2ecc71"
        elif sent_score < -0.1: sent_color_hex = "#e74c3c"

        # Inject CSS Dinamis
        st.markdown(get_dynamic_css(sent_color_hex), unsafe_allow_html=True)

        # --- BAGIAN 1: HERO SECTION SINYAL ---
        st.markdown(f"""
        <div class="signal-box" style="background-color: {signal_color_bg};">
            <h3 style='margin:0; color: #bbb; font-weight: 400;'>Rekomendasi Hybrid AI</h3>
            <h1 style='margin: 10px 0; font-size: 3rem;'>{signal_icon} {signal}</h1>
            <p style='margin:0; font-size: 1.2rem; color: #eee;'>Analisa: <b>{reason}</b></p>
        </div>
        """, unsafe_allow_html=True)

        # --- BAGIAN 2: KARTU METRIK PENDUKUNG ---
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('<div class="metric-container">', unsafe_allow_html=True)
            st.metric("💰 Harga Saat Ini", f"{current:,.0f}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-container">', unsafe_allow_html=True)
            st.metric("🎯 Prediksi Besok", f"{pred:,.0f}", delta=change)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col3:
            st.markdown('<div class="metric-container">', unsafe_allow_html=True)
            sent_delta_color = "off"
            if sent_score > 0.1: sent_delta_color = "normal"
            elif sent_score < -0.1: sent_delta_color = "inverse"
            st.metric("📰 Sentimen Berita Global", sent_label, delta=f"Score: {sent_score:.2f}", delta_color=sent_delta_color)
            st.markdown('</div>', unsafe_allow_html=True)

        st.write("") 

        # --- BAGIAN 3: VISUALISASI GRAFIK MODERN ---
        st.subheader(f"📈 Momentum Pergerakan {selected_asset}")
        
        df_chart = df.tail(180)
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df_chart['ds'], y=df_chart['y'],
            mode='lines',
            name='Historis (6 Bulan)',
            line=dict(color='#4EA8DE', width=3),
            fill='tozeroy',
            fillcolor='rgba(78, 168, 222, 0.2)'
        ))
        
        pred_date = df_chart['ds'].iloc[-1] + timedelta(days=1)
        fig.add_trace(go.Scatter(
            x=[pred_date], y=[pred],
            mode='markers+text',
            name='Target Besok',
            marker=dict(
                color='#FF9F1C', 
                size=18,
                line=dict(width=3, color='white'),
                symbol='diamond'
            ),
            text=[f"{pred:,.0f}"],
            textposition="top center",
            textfont=dict(color='#FF9F1C', size=14, family="Arial Black")
        ))

        fig.update_layout(
            template="plotly_dark",
            height=550,
            hovermode="x unified",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(
                showgrid=False,
                rangeselector=dict(
                    buttons=list([
                        dict(count=1, label="1M", step="month", stepmode="backward"),
                        dict(count=3, label="3M", step="month", stepmode="backward"),
                        dict(step="all", label="ALL")
                    ]),
                    bgcolor="#333",
                    activecolor="#4EA8DE"
                ),
            ),
            yaxis=dict(showgrid=True, gridcolor='#444444', gridwidth=0.5),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        st.write("") 

        # --- BAGIAN 4: BERITA TERKAIT ---
        st.subheader(f"🗞️ Berita Penggerak Pasar: {selected_asset}")
        st.caption(f"Warna garis kiri menunjukkan sentimen berita saat ini: **{sent_label}**")
        
        if news_list:
            with st.container():
                for news in news_list:
                    st.markdown(f"""
                    <div class="news-card">
                        <a href="{news['link']}" target="_blank" class="news-title">{news['title']}</a>
                        <span class="news-date">📅 Published: {news['published']}</span>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("⚠️ Tidak ditemukan berita terbaru yang relevan dalam 48 jam terakhir.")

    except Exception as e:
        st.error("Terjadi kesalahan dalam pemrosesan data.")
        with st.expander("Lihat Detail Error"):
            st.code(e)

st.markdown("---")
st.markdown("<div style='text-align: center; color: #666;'>Built with ❤️ using Python, Prophet, & Streamlit</div>", unsafe_allow_html=True)
