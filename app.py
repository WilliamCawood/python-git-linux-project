import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import requests

st.set_page_config(page_title="Finance Dashboard", layout="wide")

# ==========================================
# FONCTION DE SECOURS (Simulation)
# ==========================================
def generate_mock_data(tickers):
    """Génère des données réalistes si Yahoo bloque"""
    dates = pd.date_range(end=pd.Timestamp.today(), periods=252)
    mock_data = pd.DataFrame(index=dates)
    
    for ticker in tickers:
        # Simulation d'une marche aléatoire (Random Walk)
        # On part de 100 et on ajoute des variations aléatoires
        volatility = 0.02
        changes = np.random.normal(loc=0.0005, scale=volatility, size=len(dates))
        price_path = 100 * np.exp(np.cumsum(changes))
        mock_data[ticker] = price_path
        
    return mock_data

# ==========================================
# MODULE QUANT A
# ==========================================
def run_quant_a_module():
    st.header("Quant A: Single Asset Analysis")
    st.info("Espace réservé au module Single Asset.")

# ==========================================
# MODULE QUANT B (Avec Secours Automatique)
# ==========================================
def run_quant_b_module():
    st.header("Quant B: Multi-Asset Portfolio Management")
    
    tickers = st.multiselect(
        "Select Assets (min 3)", 
        ["BTC-USD", "ETH-USD", "SPY", "QQQ", "AAPL", "MSFT", "TSLA", "GLD", "EURUSD=X"],
        default=["SPY", "AAPL", "MSFT"]
    )
    
    if st.button("Analyze Portfolio"):
        if len(tickers) < 3:
            st.error("Please select at least 3 assets.")
            return

        data = pd.DataFrame()
        using_mock = False

        with st.spinner('Fetching data...'):
            try:
                # TENTATIVE 1 : Téléchargement réel
                raw_data = yf.download(tickers, period="1y", interval="1d", group_by='ticker', threads=False, progress=False)
                
                # Extraction des données complexe de yfinance
                for t in tickers:
                    try:
                        if not raw_data.empty:
                            if isinstance(raw_data.columns, pd.MultiIndex):
                                if t in raw_data.columns.get_level_values(0):
                                    data[t] = raw_data[t]['Close']
                            elif 'Close' in raw_data.columns:
                                data[t] = raw_data['Close']
                    except:
                        pass
                
                # Si après tout ça, c'est vide, on lève une erreur pour déclencher le secours
                if data.empty or data.isna().all().all():
                    raise ValueError("Yahoo download returned empty data")

            except Exception as e:
                # TENTATIVE 2 : MODE SECOURS
                using_mock = True
                data = generate_mock_data(tickers)
        
        # --- Affichage des résultats ---
        if using_mock:
            st.warning("⚠️ Impossible de contacter Yahoo Finance (Blocage SSL/Réseau). Affichage de **données simulées** pour démonstration.")
        else:
            st.success("✅ Data loaded successfully from Yahoo!")

        # Nettoyage
        data = data.dropna()

        # 1. Graphique Prix Normalisés
        st.subheader("Normalized Prices (Base 100)")
        normalized = data / data.iloc[0] * 100
        st.line_chart(normalized)

        # 2. Matrice de Corrélation
        st.subheader("Correlation Matrix")
        returns = data.pct_change().dropna()
        corr = returns.corr()
        
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f", ax=ax)
        st.pyplot(fig)

# ==========================================
# NAVIGATION
# ==========================================
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Single Asset (Quant A)", "Portfolio (Quant B)"])

if page == "Single Asset (Quant A)":
    run_quant_a_module()
elif page == "Portfolio (Quant B)":
    run_quant_b_module()