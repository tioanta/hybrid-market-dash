# --- KONFIGURASI ASET ---
ASSETS = {
    'USD': {'ticker': 'USDIDR=X', 'type': 'forex', 'keyword': 'USD IDR currency'},
    'JPY': {'ticker': 'JPYIDR=X', 'type': 'forex', 'keyword': 'JPY IDR currency'},
    'KRW': {'ticker': 'KRWIDR=X', 'type': 'forex', 'keyword': 'South Korean Won IDR currency'},
    'BBRI': {'ticker': 'BBRI.JK', 'type': 'stock', 'keyword': 'Bank BRI Indonesia stock'},
    'TLKM': {'ticker': 'TLKM.JK', 'type': 'stock', 'keyword': 'Telkom Indonesia stock'},
    'BBCA': {'ticker': 'BBCA.JK', 'type': 'stock', 'keyword': 'Bank BCA Indonesia stock'},
    'BMRI': {'ticker': 'BMRI.JK', 'type': 'stock', 'keyword': 'Bank Mandiri Indonesia stock'}
}

# --- DAFTAR KANDIDAT BLUE CHIPS (Untuk Portfolio Opt) ---
BLUE_CHIPS_CANDIDATES = [
    'BBCA.JK', 'BBRI.JK', 'BMRI.JK', 'BBNI.JK', 
    'TLKM.JK', 'ASII.JK', 'ICBP.JK', 'UNVR.JK', 
    'ADRO.JK', 'PTBA.JK', 'GOTO.JK', 'KLBF.JK'
]

# --- WARNA VISUALISASI ---
COLORS = {
    'BELI': '#2ecc71', 
    'JUAL': '#e74c3c', 
    'HOLD': '#95a5a6'
}

# --- BANK PERTANYAAN ---
QUESTIONS = [
    "Saham atau Forex, mana yang bikin cuan hari ini? 🤔",
    "Sentimen berita lagi panas! Apa strategimu? 🔥",
    "BBCA & BMRI lagi jadi sorotan, tim serok atau tim kabur? 🏃‍♂️",
    "Menurutmu analisa berita ngaruh banget gak sih ke harga? 📰",
    "Ada yang portofolionya hijau royo-royo hari ini? 🍀",
    "Pasar lagi volatile, mending wait & see atau hajar kanan? 👊"
]
