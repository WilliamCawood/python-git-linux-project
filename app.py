import streamlit as st
import yfinance as yf

st.title("Project: Python, Git, Linux for Finance - Dashboard")
symbol = st.text_input("Asset symbol", "BTC-USD")
data = yf.download(symbol,period="1y", interval="1d")
st.write("Latest price :", round(data["Close"].iloc[-1],2))
st.line_chart(data["Close"])
