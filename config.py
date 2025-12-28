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

# --- WARNA VISUALISASI ---
COLORS = {
    'BELI': '#2ecc71', # Hijau
    'JUAL': '#e74c3c', # Merah
    'HOLD': '#95a5a6'  # Abu-abu
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
