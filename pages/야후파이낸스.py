import streamlit as st
import yfinance as yf
import plotly.graph_objs as go
import pandas as pd

top_10_tickers = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA",
    "NVDA", "META", "BRK.B", "V", "JPM"
]

st.title("Global Top 10 Market Cap Stocks - 1 Year Price Change")
st.write("이 앱은 글로벌 시가총액 상위 10개 기업의 최근 1년 동안의 주식 변화를 시각화합니다.")

data = {}
error_tickers = []

for ticker in top_10_tickers:
    try:
        df = yf.download(ticker, period="1y", threads=False)
        st.write(f"📊 {ticker} 데이터 구조: {df.columns.tolist()}")
        if not df.empty and "Adj Close" in df.columns:
            data[ticker] = df["Adj Close"]
        elif not df.empty and "Close" in df.columns:
            data[ticker] = df["Close"]
            st.warning(f"⚠️ {ticker}에는 'Adj Close'가 없어 'Close'로 대체했습니다.")
        else:
            st.warning(f"⚠️ {ticker} 데이터가 없거나 'Adj Close'/'Close' 컬럼이 없습니다. (건너뜀)")
            error_tickers.append(ticker)
    except Exception as e:
        st.error(f"❌ {ticker} 데이터 로드 중 오류: {e}")
        error_tickers.append(ticker)

if data:
    # Series끼리 outer join으로 통합, 결측치는 그대로 둠
    df_all = pd.concat(data.values(), axis=1, keys=data.keys()).sort_index()
    fig = go.Figure()
    for ticker in df_all.columns:
        fig.add_trace(go.Scatter(
            x=df_all.index, y=df_all[ticker],
            mode='lines', name=ticker
        ))
    fig.update_layout(
        title="Top 10 Market Cap Stocks - 1 Year Price Change",
        xaxis_title="Date",
        yaxis_title="Adjusted Close/Close Price (USD)",
        template="plotly_dark"
    )
    st.plotly_chart(fig, use_container_width=True)
    st.success(f"성공적으로 데이터를 가져온 티커: {', '.join(data.keys())}")
else:
    st.error("데이터를 불러오지 못했습니다. (네트워크/야후 정책/환경 문제 가능성)")

if error_tickers:
    st.info(f"아래 티커는 데이터를 불러오지 못했습니다: {', '.join(error_tickers)}")
