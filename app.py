import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Finance Dashboard", layout="wide")

# ==========================================
# FONCTION 1 : Le module de William (Quant A)
# ==========================================
def run_quant_a_module():
    st.header("Quant A: Single Asset Analysis")
    st.write("Espace réservé au module de William.")
    # On laisse ça vide ou simple pour l'instant pour ne pas créer d'erreurs
    st.info("Ce module sera intégré par le Quant A.")

# ==========================================
# FONCTION 2 : Ton module (Quant B)
# ==========================================
def run_quant_b_module():
    st.header("Quant B: Multi-Asset Portfolio Management")
    
    # 1. Sélecteur d'actifs (Multiselect pour le portefeuille)
    tickers = st.multiselect(
        "Select Assets (min 3)", 
        ["BTC-USD", "ETH-USD", "SPY", "QQQ", "AAPL", "MSFT", "TSLA", "GLD", "EURUSD=X"],
        default=["SPY", "AAPL", "MSFT"]
    )
    
    # 2. Bouton de lancement
    if st.button("Analyze Portfolio"):
        if len(tickers) < 3:
            st.error("Please select at least 3 assets.")
        else:
            with st.spinner('Downloading data...'):
                # Téléchargement des données ajustées
                data = yf.download(tickers, period="1y", interval="1d")['Close']
            
            st.success("Data loaded!")
            
            # Affichage rapide pour vérifier que ça marche
            st.subheader("Raw Prices")
            st.line_chart(data)

# ==========================================
# NAVIGATION (Barre latérale)
# ==========================================
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Single Asset (Quant A)", "Portfolio (Quant B)"])

if page == "Single Asset (Quant A)":
    run_quant_a_module()
elif page == "Portfolio (Quant B)":
    run_quant_b_module()
