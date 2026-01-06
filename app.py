import streamlit as st
import yfinance as yf
import pandas as pd

st.title("Project: Python, Git, Linux for Finance - Dashboard")

st.subheader("Asset selection")

preset_tickers = {
    "Bitcoin (BTC-USD)": "BTC-USD",
    "Ethereum (ETH-USD)": "ETH-USD",
    "Solana (SOL-USD)": "SOL-USD",
    "S&P 500 ETF (SPY)": "SPY",
    "NASDAQ 100 ETF (QQQ)": "QQQ",
    "Dow Jones ETF (DIA)": "DIA",
    "MSCI World ETF (URTH)": "URTH",
    "Apple (AAPL)": "AAPL",
    "Microsoft (MSFT)": "MSFT",
    "Tesla (TSLA)": "TSLA",
    "NVIDIA (NVDA)": "NVDA",
    "Engie (ENGI.PA)": "ENGI.PA",
    "TotalEnergies (TTE.PA)": "TTE.PA",
    "LVMH (MC.PA)": "MC.PA",
    "EUR/USD (EURUSD=X)": "EURUSD=X",
    "Gold Futures (GC=F)": "GC=F",
    "Crude Oil WTI (CL=F)": "CL=F",
}

choice = st.selectbox("Choose an asset", list(preset_tickers.keys()))
symbol = preset_tickers[choice]

st.markdown("---")
st.subheader("Custom ticker (optional)")
use_custom = st.checkbox("Use a custom Yahoo Finance ticker")

if use_custom:
    symbol = st.text_input("Custom ticker", symbol).strip().upper()

st.markdown("---")
interval = st.selectbox("Data interval", ["5m", "15m", "1h", "1d"], index=0)

if interval in ["5m", "15m"]:
    period_options = ["1d", "5d", "1mo", "3mo", "6mo"]
elif interval == "1h":
    period_options = ["5d", "1mo", "3mo", "6mo", "1y"]
else:
    period_options = ["1mo", "3mo", "6mo", "1y", "2y", "5y"]

period = st.selectbox("History window", period_options, index=1)

strategy = st.selectbox("Strategy", ["Buy & Hold", "Moving Average"])

if strategy == "Moving Average":
    st.slider("MA window", 5, 200, 20)

st.info("UI scaffold ready. Data retrieval, strategies, metrics and charts will be added in the next commits.")



st.subheader("Latest price")
data = yf.download(symbol,period=period,interval=interval,auto_adjust=True,progress=False)


if isinstance(data.columns, pd.MultiIndex):
    data.columns = data.columns.get_level_values(0)

data = data.dropna()

if data.empty or "Close" not in data.columns:
    st.error("No data returned for this selection.")
    st.stop()

close = data["Close"]

latest_price = float(close.iloc[-1])
st.metric(label=symbol, value=f"{latest_price:,.2f}")

st.info("Live data retrieval connected. Strategies and charts will be added next.")
