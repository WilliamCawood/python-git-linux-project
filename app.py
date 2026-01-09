import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="Finance Dashboard", layout="wide")

# ==========================================
# FALLBACK DATA (SIMULATION)
# ==========================================
def generate_mock_data(tickers):
    dates = pd.date_range(end=pd.Timestamp.today(), periods=252)
    mock_data = pd.DataFrame(index=dates)

    for ticker in tickers:
        volatility = 0.02
        changes = np.random.normal(0.0005, volatility, len(dates))
        prices = 100 * np.exp(np.cumsum(changes))
        mock_data[ticker] = prices

    return mock_data


# ==========================================
# METRICS HELPERS (Quant A)
# ==========================================
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


def periods_per_year_from_interval(interval: str) -> int:
    if interval == "1d":
        return 252
    if interval == "1h":
        return 24 * 365
    if interval == "15m":
        return 4 * 24 * 365
    return 12 * 24 * 365  # 5m


# ==========================================
# MODULE QUANT A
# ==========================================
def run_quant_a_module():
    st.header("Quant A: Single Asset Analysis")

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
        "TotalEnergies (TTE.PA)": "TTE.PA",
        "EUR/USD (EURUSD=X)": "EURUSD=X",
        "Gold Futures (GC=F)": "GC=F",
        "Crude Oil WTI (CL=F)": "CL=F",
    }

    choice = st.selectbox("Choose an asset", list(preset_tickers.keys()), key="qa_choice")
    symbol = preset_tickers[choice]

    st.markdown("---")
    use_custom = st.checkbox("Use a custom Yahoo Finance ticker", key="qa_custom")
    if use_custom:
        symbol = st.text_input("Custom ticker", symbol, key="qa_custom_text").strip().upper()

    st.markdown("---")
    interval = st.selectbox("Data interval", ["5m", "15m", "1h", "1d"], index=0, key="qa_interval")

    # Safer period options per interval (Yahoo limits)
    if interval in ["5m", "15m"]:
        period_options = ["1d", "5d", "1mo", "3mo", "6mo"]
    elif interval == "1h":
        period_options = ["5d", "1mo", "3mo", "6mo", "1y"]
    else:
        period_options = ["1mo", "3mo", "6mo", "1y", "2y", "5y"]

    period = st.selectbox("History window", period_options, index=1, key="qa_period")

    strategy = st.selectbox("Strategy", ["Buy & Hold", "Moving Average"], key="qa_strategy")
    ma_window = 20
    if strategy == "Moving Average":
        ma_window = st.slider("MA window", 5, 200, 20, key="qa_ma")

    # Data download
    data = yf.download(symbol, period=period, interval=interval, auto_adjust=True, progress=False)

    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    data = data.dropna()
    if data.empty or "Close" not in data.columns:
        st.error("No data returned for this selection.")
        return

    close = data["Close"].dropna()
    returns = close.pct_change()

    # Strategy
    if strategy == "Buy & Hold":
        strat_returns = returns
        equity = (1 + strat_returns).cumprod()
        equity_name = "Buy & Hold equity"
    else:
        ma = close.rolling(ma_window).mean()
        signal = (close > ma).astype(int)
        strat_returns = signal.shift(1) * returns
        equity = (1 + strat_returns).cumprod()
        equity_name = f"MA({ma_window}) equity"

    # Latest price
    st.subheader("Latest price")
    st.metric(label=symbol, value=f"{float(close.iloc[-1]):,.2f}")

    # Metrics
    ppy = periods_per_year_from_interval(interval)
    equity_clean = equity.dropna()

    total_return = float(equity_clean.iloc[-1] - 1.0) if not equity_clean.empty else np.nan
    mdd = max_drawdown(equity)
    vol = annualized_vol(strat_returns, ppy)
    sh = sharpe_ratio(strat_returns, ppy)

    st.subheader("Performance metrics")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total return", f"{total_return*100:.2f}%")
    c2.metric("Max drawdown", f"{mdd*100:.2f}%")
    c3.metric("Volatility (ann.)", f"{vol*100:.2f}%")
    c4.metric("Sharpe", f"{sh:.2f}")

    # Chart
    st.subheader("Price and strategy equity curve")
    price_norm = close / close.iloc[0]
    chart_df = pd.DataFrame(
        {
            "Price (normalized)": price_norm,
            equity_name: equity,
        }
    ).dropna()

    st.line_chart(chart_df)


# ==========================================
# MODULE QUANT B (WORKING + WEIGHTS + METRICS)
# ==========================================
def run_quant_b_module():
    st.header("Quant B: Multi-Asset Portfolio Management")

    tickers = st.multiselect(
        "Select Assets (min 3)",
        ["BTC-USD", "ETH-USD", "SPY", "QQQ", "AAPL", "MSFT", "TSLA", "GLD", "EURUSD=X"],
        default=["SPY", "AAPL", "MSFT"],
        key="qb_tickers"
    )

    if len(tickers) == 0:
        st.info("Select tickers to configure portfolio weights.")
        return

    st.subheader("Portfolio Allocation (weights auto-normalized)")
    weights = {}
    cols = st.columns(min(len(tickers), 5))
    for i, t in enumerate(tickers):
        with cols[i % len(cols)]:
            weights[t] = st.slider(f"{t} weight", 0.0, 1.0, 1.0 / len(tickers), 0.01, key=f"w_{t}")

    total_w = float(sum(weights.values()))
    if total_w <= 0:
        st.warning("Total allocation is 0. Please assign positive weights.")
        return

    # Normalize weights to sum to 1
    weights = {t: float(w) / total_w for t, w in weights.items()}
    st.caption("Normalized weights: " + ", ".join([f"{t}={weights[t]:.2%}" for t in tickers]))

    if st.button("Analyze Portfolio", key="qb_run"):
        if len(tickers) < 3:
            st.error("Please select at least 3 assets.")
            return

        data = None
        using_mock = False

        with st.spinner("Fetching data..."):
            try:
                raw = yf.download(tickers, period="1y", interval="1d", progress=False)

                if isinstance(raw.columns, pd.MultiIndex):
                    # expected: level0=OHLCV, level1=tickers
                    if "Close" in raw.columns.get_level_values(0):
                        data = raw["Close"].copy()
                    else:
                        # alternative shape
                        data = raw.xs("Close", axis=1, level=1, drop_level=True)
                else:
                    # rare for multiple tickers
                    if "Close" in raw.columns:
                        data = pd.DataFrame({tickers[0]: raw["Close"]})

                if data is None or data.empty or data.isna().all().all():
                    raise ValueError("Yahoo download returned empty data")

            except Exception:
                using_mock = True
                data = generate_mock_data(tickers)

        if using_mock:
            st.warning("⚠️ Yahoo Finance unavailable — showing **simulated data** for demonstration.")
        else:
            st.success("✅ Data loaded successfully from Yahoo Finance.")

        data = data.dropna(how="any")

        # Keep only columns that exist (avoid KeyError)
        available = [t for t in tickers if t in data.columns]
        if len(available) < 3:
            st.error("Not enough assets with valid data returned. Try different tickers.")
            return
        data = data[available]
        weights = {t: weights[t] for t in available}

        # Renormalize again after dropping unavailable tickers
        s = sum(weights.values())
        weights = {t: weights[t] / s for t in available}

        if data.empty:
            st.error("No overlapping data available after cleaning.")
            return

        # Normalized asset curves (base 100)
        normalized_assets = data / data.iloc[0] * 100

        # Portfolio curve (weighted sum of normalized assets)
        portfolio_curve = pd.Series(0.0, index=normalized_assets.index, name="PORTFOLIO")
        for t in normalized_assets.columns:
            portfolio_curve += normalized_assets[t] * weights.get(t, 0.0)

        # Charts
        st.subheader("Portfolio Performance vs Individual Assets (Base 100)")
        chart_df = normalized_assets.copy()
        chart_df["PORTFOLIO"] = portfolio_curve
        st.line_chart(chart_df)

        # Portfolio Metrics
        st.subheader("Portfolio Metrics")
        port_ret = portfolio_curve.pct_change().dropna()

        total_ret = (portfolio_curve.iloc[-1] / portfolio_curve.iloc[0]) - 1.0
        vol = float(port_ret.std() * np.sqrt(252)) if not port_ret.empty else np.nan

        if port_ret.empty or float(port_ret.std()) == 0.0:
            sh = np.nan
        else:
            sh = float((port_ret.mean() / port_ret.std()) * np.sqrt(252))

        m1, m2, m3 = st.columns(3)
        m1.metric("Portfolio Total Return", f"{total_ret:.2%}")
        m2.metric("Portfolio Volatility (ann.)", f"{vol:.2%}" if not np.isnan(vol) else "N/A")
        m3.metric("Sharpe Ratio", f"{sh:.2f}" if not np.isnan(sh) else "N/A")

        # Correlation Matrix
        st.subheader("Correlation Matrix")
        returns = data.pct_change().dropna()
        corr = returns.corr()
        st.dataframe(corr.style.background_gradient(cmap="coolwarm").format("{:.2f}"))


# ==========================================
# NAVIGATION
# ==========================================
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Single Asset (Quant A)", "Portfolio (Quant B)"], key="nav")

if page == "Single Asset (Quant A)":
    run_quant_a_module()
else:
    run_quant_b_module()
