import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
from datetime import timedelta
import config
import market_analysis
import portfolio_optimizer # Import modul baru

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Hybrid Market Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- FUNGSI CSS ---
def get_dynamic_css(sentiment_color):
    return f"""
    <style>
        .news-card {{
            padding: 15px; border-radius: 12px; background-color: #1E1E24;
            margin-bottom: 12px; border-left: 6px solid {sentiment_color};
            box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: transform 0.2s;
        }}
        .news-card:hover {{ transform: translateY(-3px); }}
        .news-title {{ font-size: 16px; font-weight: 600; color: #EAEAEA; text-decoration: none; display: block; margin-bottom: 8px; }}
        .news-title:hover {{ color: #4EA8DE; }}
        .news-date {{ font-size: 12px; color: #888888; font-style: italic; }}
        .signal-box {{
            padding: 25px; border-radius: 20px; text-align: center; margin-bottom: 25px;
            backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.1);
        }}
        .metric-container {{ background-color: #1E1E24; padding: 20px; border-radius: 15px; text-align: center; border: 1px solid #333; }}
        /* CSS Khusus Portfolio */
        .portfolio-card {{ background-color: #2b2d42; padding: 20px; border-radius: 15px; border: 1px solid #4EA8DE; text-align: center; }}
    </style>
    """

# --- CACHE ---
@st.cache_data(ttl=3600)
def load_market_data(ticker, keyword):
    df, current, pred = market_analysis.get_technical_forecast(ticker)
    if df is None: return None, None, None, None, None, None, None, None, None
    sent_score, sent_label, news_list = market_analysis.get_news_sentiment(keyword)
    signal, change, reason = market_analysis.get_hybrid_signal(current, pred, sent_score)
    return df, current, pred, sent_score, sent_label, news_list, signal, change, reason

# --- MAIN DASHBOARD ---
st.title("⚡ Hybrid Market Intelligence")
st.markdown("### *Technical Data + News Sentiment + Portfolio AI*")

# --- TAB NAVIGASI ---
tab1, tab2 = st.tabs(["📊 Market Analysis", "💼 Portfolio Generator (Robo-Advisor)"])

# =========================================
# TAB 1: MARKET ANALYSIS (Fitur Lama)
# =========================================
with tab1:
    # --- SIDEBAR KHUSUS TAB 1 ---
    st.sidebar.header("🎯 Kontrol Aset")
    input_mode = st.sidebar.radio("Metode Pencarian:", ["Daftar Populer", "Cari Manual (Custom)"])
    
    target_ticker = ""
    target_keyword = ""
    display_name = ""

    if input_mode == "Daftar Populer":
        selected_asset = st.sidebar.selectbox("Pilih Aset:", list(config.ASSETS.keys()), index=0)
        target_ticker = config.ASSETS[selected_asset]['ticker']
        target_keyword = config.ASSETS[selected_asset]['keyword']
        display_name = selected_asset
    else:
        st.sidebar.info("Tips: Gunakan akhiran .JK untuk saham Indonesia.")
        target_ticker = st.sidebar.text_input("Kode Saham:", value="GOTO.JK").upper()
        target_keyword = st.sidebar.text_input("Keyword Berita:", value="GoTo Stock")
        display_name = target_ticker

    if st.sidebar.button("🔄 Refresh Data", type="primary"):
        st.cache_data.clear()
        st.rerun()

    if target_ticker:
        with st.spinner(f"🤖 Menganalisa {display_name}..."):
            try:
                df, current, pred, sent_score, sent_label, news_list, signal, change, reason = load_market_data(target_ticker, target_keyword)
                
                if df is not None:
                    # Logic Warna & CSS (Sama seperti sebelumnya)
                    signal_bg = "rgba(46, 204, 113, 0.2)" if "BUY" in signal else ("rgba(231, 76, 60, 0.2)" if "SELL" in signal else "#333")
                    sent_hex = "#2ecc71" if sent_score > 0.1 else ("#e74c3c" if sent_score < -0.1 else "#95a5a6")
                    st.markdown(get_dynamic_css(sent_hex), unsafe_allow_html=True)

                    # Hero Section
                    st.markdown(f"""
                    <div class="signal-box" style="background-color: {signal_bg};">
                        <h3 style='margin:0; color: #bbb;'>Rekomendasi Hybrid AI: {display_name}</h3>
                        <h1 style='margin: 10px 0; font-size: 3rem;'>{signal}</h1>
                        <p style='margin:0; font-size: 1.2rem; color: #eee;'>Analisa: <b>{reason}</b></p>
                    </div>
                    """, unsafe_allow_html=True)

                    # Metrics & Chart
                    c1, c2, c3 = st.columns(3)
                    with c1: st.metric("💰 Harga", f"{current:,.0f}")
                    with c2: st.metric("🎯 Target", f"{pred:,.0f}", delta=change)
                    with c3: st.metric("📰 Sentimen", sent_label, delta=f"{sent_score:.2f}")

                    st.subheader(f"📈 Momentum: {display_name}")
                    df_chart = df.tail(180)
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=df_chart['ds'], y=df_chart['y'], mode='lines', name='Historis', line=dict(color='#4EA8DE', width=3), fill='tozeroy', fillcolor='rgba(78, 168, 222, 0.2)'))
                    fig.add_trace(go.Scatter(x=[df_chart['ds'].iloc[-1] + timedelta(days=1)], y=[pred], mode='markers+text', name='Target', marker=dict(color='#FF9F1C', size=18, symbol='diamond'), text=[f"{pred:,.0f}"], textposition="top center"))
                    fig.update_layout(template="plotly_dark", height=450, hovermode="x unified", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig, use_container_width=True)

                    # News
                    st.subheader("🗞️ Berita Terkait")
                    if news_list:
                        for news in news_list:
                            st.markdown(f"<div class='news-card'><a href='{news['link']}' target='_blank' class='news-title'>{news['title']}</a><span class='news-date'>{news['published']}</span></div>", unsafe_allow_html=True)
                    else:
                        st.warning("Tidak ada berita terbaru.")
                else:
                    st.error("Data tidak ditemukan.")
            except Exception as e:
                st.error(f"Error: {e}")

# =========================================
# TAB 2: PORTFOLIO GENERATOR (Fitur Baru)
# =========================================
with tab2:
    st.header("💼 Robo-Advisor: Daily Top 4 Portfolio")
    st.markdown("""
    Fitur ini menggunakan algoritma **Modern Portfolio Theory (Optimization)** untuk:
    1. Memindai saham Blue Chip LQ45.
    2. Memilih 4 saham dengan kinerja Risk/Reward terbaik saat ini.
    3. Menghitung alokasi optimal sesuai dana investasi Anda.
    """)
    st.markdown("---")

    # Input Dana
    col_input1, col_input2 = st.columns([2, 1])
    with col_input1:
        investment_amount = st.number_input("💰 Masukkan Dana Investasi (IDR):", min_value=1000000, value=10000000, step=500000)
    with col_input2:
        st.write("") # Spacer
        st.write("") 
        generate_btn = st.button("🚀 Generate Rekomendasi", type="primary", use_container_width=True)

    if generate_btn:
        with st.spinner("🔄 Sedang menghitung Sharpe Ratio & Optimasi Bobot..."):
            recs, total_est = portfolio_optimizer.get_optimized_portfolio(investment_amount)
            
            if recs:
                st.success(f"Optimasi Selesai! Estimasi Pemakaian Dana: Rp {total_est:,.0f} (Sisa uang masuk RDN)")
                
                # Visualisasi Donut Chart Alokasi
                df_recs = pd.DataFrame(recs)
                
                col_chart, col_table = st.columns([1, 1])
                
                with col_chart:
                    st.subheader("🍰 Alokasi Aset")
                    fig_pie = px.pie(df_recs, values='Allocation (IDR)', names='Ticker', hole=0.4, 
                                     color_discrete_sequence=px.colors.sequential.RdBu)
                    fig_pie.update_layout(template="plotly_dark", showlegend=True)
                    st.plotly_chart(fig_pie, use_container_width=True)
                
                with col_table:
                    st.subheader("📋 Daftar Belanja (Action Plan)")
                    for rec in recs:
                        st.markdown(f"""
                        <div class="portfolio-card">
                            <h2 style="margin:0; color:#4EA8DE;">{rec['Ticker']}</h2>
                            <p style="color:#aaa;">Harga: {rec['Price']:,.0f}</p>
                            <hr style="border-color:#555;">
                            <h3 style="margin:0; color:#fff;">Beli: {rec['Buy (Lots)']} Lot</h3>
                            <p style="margin:0; font-size:0.9em; color:#2ecc71;">(Rp {rec['Est. Value (IDR)']:,.0f})</p>
                        </div>
                        <br>
                        """, unsafe_allow_html=True)
                
                # Detail Dataframe
                with st.expander("Lihat Detail Perhitungan Matematis"):
                    st.dataframe(df_recs)
            else:
                st.error("Gagal melakukan optimasi. Coba lagi nanti.")

st.markdown("---")
st.markdown("<div style='text-align: center; color: #666;'>Built with ❤️ using Python, Prophet, & Streamlit</div>", unsafe_allow_html=True)