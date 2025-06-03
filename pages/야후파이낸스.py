import streamlit as st
import yfinance as yf
import plotly.graph_objs as go
import pandas as pd

# 글로벌 시가총액 상위 10개 기업 티커
top_10_tickers = [
    "AAPL",  # Apple
    "MSFT",  # Microsoft
    "GOOGL", # Alphabet (Google) - Class A
    "AMZN",  # Amazon
    "TSLA",  # Tesla
    "NVDA",  # NVIDIA
    "META",  # Meta (Facebook)
    "BRK-B", # Berkshire Hathaway (Class B)
    "V",     # Visa
    "JPM"    # JPMorgan Chase
]

st.title("Global Top 10 Market Cap Stocks - 1 Year Price Change")
st.write("이 앱은 글로벌 시가총액 상위 10개 기업의 최근 1년 동안의 주식 변화를 시각화합니다.")

data = {}

# 데이터 수집
for ticker in top_10_tickers:
    df = yf.download(ticker, period="1y")
    # 예외처리: 데이터가 비어있지 않고, 'Adj Close' 컬럼이 있을 때만 추가
    if not df.empty and "Adj Close" in df.columns:
        data[ticker] = df["Adj Close"]
    else:
        st.warning(f"⚠️ {ticker} 데이터가 없거나 'Adj Close' 컬럼이 없습니다. (건너뜀)")

# 시각화
if data:
    df_all = pd.DataFrame(data)
    fig = go.Figure()
    for ticker in df_all.columns:
        fig.add_trace(go.Scatter(
            x=df_all.index, y=df_all[ticker],
            mode='lines', name=ticker
        ))
    fig.update_layout(
        title="Top 10 Market Cap Stocks - 1 Year Price Change",
        xaxis_title="Date",
        yaxis_title="Adjusted Close Price (USD)",
        template="plotly_dark"
    )
    s
