import streamlit as st
import yfinance as yf
import plotly.graph_objs as go
import pandas as pd

# 글로벌 시가총액 상위 10개 기업 티커 (예시)
top_10_tickers = [
    "AAPL",  # Apple
    "MSFT",  # Microsoft
    "GOOGL",  # Alphabet (Google)
    "AMZN",  # Amazon
    "TSLA",  # Tesla
    "NVDA",  # NVIDIA
    "META",  # Meta (Facebook)
    "BRK-B",  # Berkshire Hathaway
    "V",  # Visa
    "JPM"   # JPMorgan Chase
]

# 제목 설정
st.title("Global Top 10 Market Cap Stocks - 1 Year Price Change")
st.write("이 앱은 글로벌 시가총액 상위 10개 기업의 최근 1년 동안의 주식 변화를 시각화합니다.")

# 최근 1년 데이터 가져오기
data = {}
for ticker in top_10_tickers:
    data[ticker] = yf.download(ticker, period="1y")["Adj Close"]

# 데이터 프레임으로 변환
df = pd.DataFrame(data)

# Plotly 그래프 그리기
fig = go.Figure()

# 각 종목에 대해 라인 추가
for ticker in top_10_tickers:
    fig.add_trace(go.Scatter(
        x=df.index, y=df[ticker],
        mode='lines', name=ticker
    ))

# 레이아웃 설정
fig.update_layout(
    title="Top 10 Market Cap Stocks - 1 Year Price Change",
    xaxis_title="Date",
    yaxis_title="Adjusted Close Price (USD)",
    template="plotly_dark"
)

# 그래프를 스트림릿에 표시
st.plotly_chart(fig)
