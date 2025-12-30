import yfinance as yf
import pandas as pd
import numpy as np
from scipy.optimize import minimize
import config

def get_optimized_portfolio(investment_amount):
    """
    1. Ambil data Blue Chips.
    2. Pilih 4 dengan Sharpe Ratio terbaik.
    3. Optimasi bobot alokasi.
    4. Hitung jumlah lot.
    """
    try:
        tickers = config.BLUE_CHIPS_CANDIDATES
        
        # 1. Ambil Data (6 Bulan Terakhir)
        df = yf.download(tickers, period="6mo", progress=False)['Close']
        
        if df.empty: return None, "Gagal mengambil data saham."

        # Hitung Daily Returns
        returns = df.pct_change().dropna()

        # 2. Screening: Cari 4 Saham dengan Sharpe Ratio Tertinggi
        # Sharpe = Rata-rata Return / Standar Deviasi (Risiko)
        mean_returns = returns.mean()
        std_dev = returns.std()
        sharpe_ratios = mean_returns / std_dev
        
        # Ambil 4 terbaik
        top_4_tickers = sharpe_ratios.nlargest(4).index.tolist()
        
        # Filter data hanya untuk Top 4
        selected_returns = returns[top_4_tickers]
        current_prices = df[top_4_tickers].iloc[-1]

        # 3. Portfolio Optimization (Minimize Volatility for Target Return)
        # Kita pakai pendekatan Maximize Sharpe Ratio sederhana
        num_assets = len(top_4_tickers)
        
        # Fungsi Negatif Sharpe (karena scipy bisanya minimize)
        def negative_sharpe(weights):
            portfolio_return = np.sum(selected_returns.mean() * weights) * 252
            portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(selected_returns.cov() * 252, weights)))
            return - (portfolio_return / portfolio_volatility)

        # Constraints: Total bobot harus 1 (100%)
        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        # Bounds: Tiap saham minimal 5%, maksimal 50% (agar diversifikasi terjaga)
        bounds = tuple((0.05, 0.5) for _ in range(num_assets))
        
        # Initial Guess (Bagi rata)
        init_guess = [1/num_assets] * num_assets

        # Eksekusi Optimasi
        result = minimize(negative_sharpe, init_guess, method='SLSQP', bounds=bounds, constraints=constraints)
        optimal_weights = result.x

        # 4. Susun Hasil Rekomendasi
        recommendations = []
        total_spent = 0
        
        for i, ticker in enumerate(top_4_tickers):
            weight = optimal_weights[i]
            allocated_money = investment_amount * weight
            price = current_prices[ticker]
            
            # Hitung Lot (1 Lot = 100 Lembar)
            # Dibulatkan ke bawah agar tidak melebihi budget
            lots = int(allocated_money / (price * 100))
            if lots < 1: lots = 0 # Kalau uang gak cukup
            
            actual_value = lots * 100 * price
            
            recommendations.append({
                'Ticker': ticker,
                'Price': price,
                'Weight (%)': round(weight * 100, 2),
                'Allocation (IDR)': allocated_money,
                'Buy (Lots)': lots,
                'Est. Value (IDR)': actual_value
            })
            total_spent += actual_value

        return recommendations, total_spent

    except Exception as e:
        print(f"Error Optimization: {e}")
        return None, str(e)