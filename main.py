import streamlit as st
import folium
from streamlit_folium import st_folium

# 미국 50개 주의 이름과 위도, 경도 데이터 (예시로 몇 개만 추가)
states_data = {
    "Alabama": [32.806671, -86.791130],
    "Alaska": [61.370716, -149.493686],
    "Arizona": [33.729759, -111.431221],
    "Arkansas": [34.969704, -92.373123],
    "California": [36.116203, -119.681564],
    "Colorado": [39.059811, -105.311104],
    "Connecticut": [41.597782, -72.755371],
    "Delaware": [38.66597, -75.74319],
    "Florida": [27.766279, -81.686783],
    "Georgia": [33.040619, -83.643074],
    "Hawaii": [21.094318, -157.498337],
    # ... (나머지 40개 주를 여기에 추가하세요)
}

# 스트림릿 앱 제목
st.title("🇺🇸 미국 50개 주 지도")

# 상태 선택
state = st.selectbox("주를 선택하세요:", list(states_data.keys()))

# 선택된 주의 위도와 경도
lat, lon = states_data[state]

# 지도 생성
m = folium.Map(location=[lat, lon], zoom_start=5)

# 선택된 주에 마커 추가
folium.Marker([lat, lon], tooltip=state).add_to(m)

# 지도 표시
st_folium(m, width=700, height=500)
