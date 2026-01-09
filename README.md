Python, git, linux ESILV module final project

The application is built with Python and Streamlit and retrieves market data using Yahoo Finance (yfinance).  
It demonstrates both single-asset quantitative analysis and multi-asset portfolio analysis of financial data.

Features

A – Single Asset Analysis
- Selection of a single financial asset (stocks, ETFs, crypto, FX, commodities)
- Live market data retrieval
- Buy & Hold strategy
- Moving Average trading strategy with adjustable window
- Performance metrics:
  - Total return
  - Maximum drawdown
  - Annualized volatility
  - Sharpe ratio
- Interactive price and equity curve visualization



B – Portfolio (Multi-Asset) Analysis
This module focuses on portfolio-level analysis using multiple assets.

Features
- Selection of multiple assets (minimum of three)
- Market data retrieval via Yahoo Finance
- Automatic fallback to simulated data if the data provider is unavailable (clearly indicated in the interface)
- Normalized price comparison across selected assets
- Correlation matrix to study diversification and asset relationships
- This module highlights portfolio diversification concepts and cross-asset correlations.



Data Source
- Provider: Yahoo Finance
- Access Method: API consumption via the yfinance Python library
- Website: https://finance.yahoo.com

Using : Python 3, Streamlit, yfinance, pandas, numpy, Git & GitHub, Linux (Ubuntu / WSL)
