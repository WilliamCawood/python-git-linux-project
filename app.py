import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

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

ma_window = 20
if strategy == "Moving Average":
   ma_window = st.slider("MA window", 5, 200, 20)



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

returns = close.pct_change()

if strategy == "Buy & Hold":
    strat_returns  = returns
    equity = (1 + returns).cumprod()
    equity_name = "Buy & Hold equity"
else:
    ma = close.rolling(ma_window).mean()
    signal = (close > ma).astype(int)       
    strat_returns = signal.shift(1) * returns
    equity = (1 + strat_returns).cumprod()
    equity_name = f"MA({ma_window}) equity"


def max_drawdown(equity_series: pd.Series) -> float:
    eq = equity_series.dropna()
    if eq.empty:
        return np.nan
    peak = eq.cummax()
    dd = eq / peak - 1.0
    return float(dd.min())

def annualized_vol(ret: pd.Series, periods_per_year: int) -> float:
    r = ret.dropna()
    if r.empty:
        return np.nan
    return float(r.std() * np.sqrt(periods_per_year))

def sharpe_ratio(ret: pd.Series, periods_per_year: int) -> float:
    r = ret.dropna()
    if r.empty:
        return np.nan
    std = float(r.std())
    if std == 0.0:
        return np.nan
    return float((r.mean() / std) * np.sqrt(periods_per_year))


if interval == "1d":
    periods_per_year = 252
elif interval == "1h":
    periods_per_year = 24 * 365
elif interval == "15m":
    periods_per_year = 4 * 24 * 365
else:
    periods_per_year = 12 * 24 * 365

equity_clean = equity.dropna()
total_return = float(equity_clean.iloc[-1] - 1.0) if not equity_clean.empty else np.nan
mdd = max_drawdown(equity)
vol = annualized_vol(strat_returns, periods_per_year)
sharpe = sharpe_ratio(strat_returns, periods_per_year)

st.subheader("Performance metrics")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total return", f"{total_return*100:.2f}%")
c2.metric("Max drawdown", f"{mdd*100:.2f}%")
c3.metric("Volatility (ann.)", f"{vol*100:.2f}%")
c4.metric("Sharpe", f"{sharpe:.2f}")


st.subheader("Price and strategy equity curve")

price_norm = close / close.iloc[0]

chart_df = pd.DataFrame(
    {
        "Price (normalized)": price_norm,
        equity_name: equity,
    }
).dropna()

st.line_chart(chart_df)
